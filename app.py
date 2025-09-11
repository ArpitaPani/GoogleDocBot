import streamlit as st
from dotenv import load_dotenv
from auth import get_google_creds, get_oauth_login_url
from drive import list_google_docs, get_doc_content
from pipeline import RAG
from utils import chunk_text

load_dotenv()

st.set_page_config(page_title="RAG Google Docs Chatbot", layout="wide")
st.title("📄 RAG Chatbot — Google Docs")

if "creds" not in st.session_state:
    st.session_state["creds"] = None
if "rag" not in st.session_state:
    st.session_state["rag"] = RAG()  # always keep one instance

creds = get_google_creds()
if creds and st.session_state["creds"] is None:
    st.session_state["creds"] = creds
    st.query_params.clear()
    st.success("✅ You are now logged in!")

col1, col2 = st.columns([1, 3])

with col1:
    st.header("Authentication")
    if st.session_state["creds"] is None:
        auth_url, _ = get_oauth_login_url()
        st.markdown(f"[🔑 Sign in with Google]({auth_url})")
    else:
        st.success("You are authenticated with Google!")

    st.markdown("---")
    st.header("Selected Docs")

    if st.session_state["creds"]:
        try:
            files = list_google_docs(st.session_state["creds"])
            names = [f"{f['name']} ({f['id']})" for f in files]
            selected = st.multiselect("Choose Docs to add to KB", options=names)

            if st.button("Add selected docs to KB"):
                chosen_ids = [s.split("(")[-1].strip(")") for s in selected]
                docs_texts, metas, skipped_docs = [], [], []

                for fid in chosen_ids:
                    txt = get_doc_content(st.session_state["creds"], fid).strip()
                    if not txt:
                        skipped_docs.append(fid)
                        continue

                    chunks = [c for c in chunk_text(txt, max_chars=1000) if c.strip()]
                    for c in chunks:
                        docs_texts.append(c)
                        metas.append({"source": fid})

                if docs_texts:
                    st.session_state["rag"].add_documents(docs_texts, metadatas=metas)
                    st.success(f"✅ Added {len(docs_texts)} text chunks to Knowledge Base")

                    if skipped_docs:
                        st.warning(f"⚠️ Skipped {len(skipped_docs)} docs with no extractable text.")
                else:
                    st.warning("⚠️ No valid text chunks found in selected docs.")

        except Exception as e:
            st.error(f"Error listing or fetching docs: {e}")
    else:
        st.info("Please sign in first to access your Google Docs.")

with col2:
    st.header("Chat")
    if not st.session_state["rag"].docs:
        st.info("Upload documents to start chatting.")
    else:
        query = st.text_input("Ask a question about your documents")
        if st.button("Ask") and query.strip():
            with st.spinner("Thinking..."):
                res = st.session_state["rag"].answer(query)
            if res["from_docs"]:
                st.success("Answer (from your documents):")
            else:
                st.warning("No relevant info found in your docs. Answer is from general knowledge.")
            st.write(res["answer"])

            # if res["source_docs"]:
            #     st.markdown("**Source doc metadata:**")
            #     st.json(res["source_docs"])

st.markdown("---")
st.caption("🔒 Authenticate -> Select Documents to add to KB -> Start your Chat.")

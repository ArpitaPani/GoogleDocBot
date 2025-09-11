import streamlit as st
from dotenv import load_dotenv

from drive import list_google_docs, get_doc_content
from pipeline import RAG
from auth import start_auth_link, exchange_code_for_credentials, credentials_from_session
from utils import chunk_text

load_dotenv()
st.set_page_config(page_title="RAG Google Docs Chatbot", layout="wide")
st.title("RAG Chatbot — Google Docs Integration (OAuth)")

if "rag" not in st.session_state:
    st.session_state["rag"] = RAG() 


creds = credentials_from_session()
if not creds:
    creds = exchange_code_for_credentials()

col1, col2 = st.columns([1, 3])

with col1:
    st.header("Authentication")

    if not creds:
        if st.button("Authenticate with Google"):
            auth_url = start_auth_link()
            st.markdown(f"[Click here to sign in with Google]({auth_url})")
        st.info("Please authenticate first")
    else:
        st.success("Authenticated ✅")

        st.markdown("---")
        st.header("Selected Docs")
        try:
            files = list_google_docs(creds)
            if not files:
                st.warning("No Google Docs found in your Drive.")
            else:
                names = [f"{f['name']} ({f['id']})" for f in files]
                selected = st.multiselect("Choose Docs to add to KB", options=names)

                if st.button("Add selected docs to KB"):
                    chosen_ids = [s.split("(")[-1].strip(")") for s in selected]
                    docs_texts, metas = [], []

                    for fid in chosen_ids:
                        txt = get_doc_content(fid, creds)
                        st.write(f"Fetched {len(txt)} characters from {fid}")
                        chunks = chunk_text(txt, max_chars=1000)
                        for c in chunks:
                            docs_texts.append(c)
                            metas.append({"source": fid})

                    if docs_texts:
                        rag = st.session_state["rag"]

                        # clearing old KB before adding new docs
                        rag.clear()
                        rag.add_documents(docs_texts, metadatas=metas)

                        st.success(
                            f"KB reset and added {len(docs_texts)} chunks. "
                            f"KB size: {rag.vectordb._collection.count()}"
                        )
                    else:
                        st.warning("No text found in selected documents.")
        except Exception as e:
            st.error(f"Error listing docs: {e}")

with col2:
    st.header("Chat")

    if st.session_state.get("rag") is None:
        st.info("Please add docs first")
    else:
        query = st.text_input("Ask a question about your documents")
        if st.button("Ask") and query.strip():
            with st.spinner("Thinking..."):
                res = st.session_state["rag"].answer(query)

            if res["from_docs"]:
                st.success("Answer (from your documents):")
            else:
                st.warning("Answer not found in documents. This is from general knowledge.")
            st.write(res["answer"])

st.markdown("---")
st.caption("This app uses Google OAuth. Sign in to access your own Docs.")

# app.py
import streamlit as st
from dotenv import load_dotenv
from drive import list_google_docs, get_doc_content
from pipeline import RAG
from auth import authenticate
from utils import chunk_text

load_dotenv()
st.set_page_config(page_title="RAG Google Docs Chatbot", layout="wide")
st.title("RAG Chatbot — Google Docs Integration")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "rag" not in st.session_state:
    st.session_state["rag"] = None

col1, col2 = st.columns([1, 3])

with col1:
    st.header("Authentication")
    if not st.session_state["authenticated"]:
        if st.button("Authenticate with Google"):
            try:
                authenticate()
                st.session_state["authenticated"] = True
                st.success("Authenticated! Token saved.")
            except Exception as e:
                st.error(f"Auth failed: {e}")
    else:
        st.success("Already authenticated.")

    st.markdown("---")
    st.header("Selected Docs")

    if st.session_state["authenticated"]:
        try:
            files = list_google_docs()
            names = [f"{f['name']} ({f['id']})" for f in files]
            selected = st.multiselect("Choose Docs to add to KB", options=names)
            if st.button("Add selected docs to KB"):
                chosen_ids = [s.split("(")[-1].strip(")") for s in selected]
                docs_texts, metas = [], []

                for fid in chosen_ids:
                    txt = get_doc_content(fid)
                    st.write(f"Fetched {len(txt)} characters from {fid}")
                    chunks = chunk_text(txt, max_chars=1000)
                    for c in chunks:
                        docs_texts.append(c)
                        metas.append({"source": fid})

                if docs_texts:
                    rag = RAG()
                    rag.add_documents(docs_texts, metadatas=metas)
                    st.session_state["rag"] = rag
                    st.success(
                        f"Added {len(docs_texts)} chunks. KB size: {rag.vectordb._collection.count()}"
                    )
                else:
                    st.warning("No text found in selected documents.")
        except Exception as e:
            st.error(f"Error listing docs: {e}")
    else:
        st.info("Please authenticate first")

with col2:
    st.header("Chat")
    if st.button("(Re)Initialize RAG"):
        st.session_state["rag"] = RAG()
        st.success("RAG initialized")

    if st.session_state.get("rag") is None:
        st.info("Initialize RAG or add docs first")
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
            # if res["source_docs"]:
            #     st.markdown("**Source doc metadata:**")
            #     st.write(res["source_docs"])

st.markdown("---")
st.caption("Tip: Run `python auth.py` manually once if browser auth fails.")

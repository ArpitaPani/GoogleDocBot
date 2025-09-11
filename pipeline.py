import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.schema import HumanMessage
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ Missing OPENAI_API_KEY in environment variables.")

CHROMA_DIR = os.environ.get("CHROMA_DB_DIR", "./storage/chromadb")


def _get_embeddings():
    return OpenAIEmbeddings()


def _get_llm():
    return ChatOpenAI(temperature=0, model="gpt-4o")


class RAG:
    def __init__(self, persist_directory=CHROMA_DIR):
        self.persist_directory = persist_directory
        os.makedirs(self.persist_directory, exist_ok=True)
        self.embeddings = _get_embeddings()
        self.llm = _get_llm()

        try:
            self.vectordb = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
        except Exception:
            # initialize empty vectorstore
            self.vectordb = Chroma.from_texts(
                [],
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )

    def add_documents(self, docs: list, metadatas: list = None):
        """Add documents to the vector store."""
        entries = [
            Document(page_content=docs[i], metadata=metadatas[i] if metadatas else {})
            for i in range(len(docs))
        ]
        self.vectordb.add_documents(entries)
        self.vectordb.persist()

    def retrieve(self, query, k=4):
        retriever = self.vectordb.as_retriever(
            search_type="similarity", search_kwargs={"k": k}
        )
        return retriever.get_relevant_documents(query)

    def answer(self, query, k=4):
        docs = self.retrieve(query, k=k)
        found = len(docs) > 0 and any(d.page_content.strip() for d in docs)
        context = "\n\n---\n\n".join([d.page_content for d in docs]) if found else ""

        if found:
            prompt = (
                f"You are a helpful assistant. Use the following DOCUMENTS to answer.\n\n"
                f"DOCUMENTS:\n{context}\n\nQUESTION: {query}"
            )
        else:
            prompt = (
                f"I couldn't find relevant information in the user's documents. "
                f"Answer from general knowledge.\n\nQUESTION: {query}"
            )

        res = self.llm.invoke([HumanMessage(content=prompt)])
        return {
            "answer": res.content if hasattr(res, "content") else str(res),
            "from_docs": found,
            "source_docs": [{"metadata": d.metadata} for d in docs]
        }

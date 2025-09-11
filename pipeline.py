import os
import numpy as np
from dotenv import load_dotenv
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.docstore.document import Document

load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


def _get_embeddings():
    if not OPENAI_API_KEY:
        raise ValueError("❌ Missing OPENAI_API_KEY in .env.")
    return OpenAIEmbeddings()


def _get_llm():
    if not OPENAI_API_KEY:
        raise ValueError("❌ Missing OPENAI_API_KEY in .env.")
    return ChatOpenAI(temperature=0, model="gpt-4o")


class RAG:
    def __init__(self):
        """Initialize RAG pipeline with in-memory embeddings (no Chroma)."""
        self.embeddings = _get_embeddings()
        self.llm = _get_llm()
        self.docs = []         # List[Document]
        self.vectors = None    # np.ndarray of embeddings
        print("✅ Initialized RAG (in-memory store)")

    def add_documents(self, docs: list, metadatas: list = None):
        """Embed and add documents in memory."""
        valid_entries = []
        for i, d in enumerate(docs):
            if d and d.strip():
                valid_entries.append(
                    Document(
                        page_content=d.strip(),
                        metadata=metadatas[i] if metadatas else {}
                    )
                )

        if not valid_entries:
            print("⚠️ No valid documents to embed. Skipping add_documents.")
            return

        texts = [d.page_content for d in valid_entries]
        new_vectors = self.embeddings.embed_documents(texts)
        new_vectors = np.array(new_vectors)

        if self.vectors is None:
            self.vectors = new_vectors
            self.docs = valid_entries
        else:
            self.vectors = np.vstack([self.vectors, new_vectors])
            self.docs.extend(valid_entries)

        print(f"✅ Added {len(valid_entries)} docs to in-memory store.")

    def retrieve(self, query, k=4):
        """Retrieve top-k similar documents using cosine similarity."""
        if self.vectors is None or not self.docs:
            return []

        query_vec = np.array(self.embeddings.embed_query(query))
        scores = np.dot(self.vectors, query_vec) / (
            np.linalg.norm(self.vectors, axis=1) * np.linalg.norm(query_vec)
        )

        top_indices = np.argsort(scores)[::-1][:k]
        return [self.docs[i] for i in top_indices]

    def answer(self, query, k=4):
        docs = self.retrieve(query, k=k)
        found = len(docs) > 0 and any(d.page_content.strip() for d in docs)
        context = "\n\n---\n\n".join([d.page_content for d in docs]) if found else ""

        prompt = (
            f"You are a helpful assistant. Use the following DOCUMENTS to answer.\n\n"
            f"DOCUMENTS:\n{context}\n\nQUESTION: {query}"
        ) if found else (
            f"I couldn't find relevant information in the user's documents. "
            f"Answer from general knowledge.\n\nQUESTION: {query}"
        )

        res = self.llm([HumanMessage(content=prompt)])
        return {
            "answer": res.content if hasattr(res, "content") else str(res),
            "from_docs": found,
            "source_docs": [{"metadata": d.metadata} for d in docs]
        }

from chromadb import Client
from chromadb.config import Settings
import os

class RAGEngine:
    def __init__(self, persist_dir: str = './api/rag/chroma_db'):
        try:
            self.client = Client(Settings(chroma_db_impl="chromadb.db.duckdb.DuckDB", persist_directory=os.path.abspath(persist_dir)))
            self.collection = self.client.get_collection('merchants')
        except Exception:
            self.client = Client(Settings(chroma_db_impl="chromadb.db.duckdb.DuckDB", persist_directory=os.path.abspath(persist_dir)))
            try:
                self.collection = self.client.create_collection('merchants')
            except Exception:
                self.collection = self.client.get_collection('merchants')

    def explain(self, text: str, category: str, k: int = 3) -> str:
        try:
            res = self.collection.query(query_texts=[text], n_results=k)
            docs = res.get('documents', [[]])[0]
            metas = res.get('metadatas', [[]])[0]
            if not docs:
                return f"No similar examples found for category {category}."
            rationale = []
            for d, m in zip(docs, metas):
                rationale.append(f"Example: '{d[:120]}' (category: {m.get('category')})")
            return ' '.join(rationale[:2])
        except Exception as e:
            return str(e)


class StubRAG:
    def __init__(self):
        pass

    def explain(self, text: str, category: str, k: int = 3) -> str:
        return f"(stub) No local RAG DB available — fallback rationale for '{category}'."

import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer
from cad_automata.config import settings
from cad_automata.logger import get_logger

logger = get_logger(__name__)

class LocalVectorStore:
    def __init__(self):
        self.model = SentenceTransformer(settings.embedding_model)
        self.conn = sqlite3.connect(settings.sqlite_db_path)
        self._init_db()

    def _init_db(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS components (
                    id TEXT PRIMARY KEY,
                    metadata TEXT,
                    file_path TEXT,
                    embedding BLOB
                )
            """)

    def add_component(self, comp_id: str, text_metadata: str, file_path: str):
        embedding = self.model.encode(text_metadata).astype(np.float32).tobytes()
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO components (id, metadata, file_path, embedding) VALUES (?, ?, ?, ?)",
                (comp_id, text_metadata, file_path, embedding)
            )
        logger.info(f"Indexed component {comp_id} into SQLite vector store.")

    def search(self, query_text: str, top_k: int = 1) -> dict:
        query_emb = self.model.encode(query_text).astype(np.float32)
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, metadata, file_path, embedding FROM components")
        
        best_match = None
        max_sim = -float("inf")

        for row in cursor.fetchall():
            comp_id, metadata, file_path, emb_blob = row
            db_emb = np.frombuffer(emb_blob, dtype=np.float32)
            sim = np.dot(query_emb, db_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(db_emb))
            if sim > max_sim:
                max_sim = sim
                best_match = {"id": comp_id, "metadata": metadata, "file_path": file_path, "similarity": float(sim)}

        logger.info(f"RAG retrieved best match: {best_match['id']} with similarity {max_sim:.4f}")
        return best_match
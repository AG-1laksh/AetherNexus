import logging
from pathlib import Path
from typing import List, Dict, Any

try:
    import chromadb
except ImportError:
    chromadb = None

from config import BASE_DIR, VECTOR_INDEX_NAME

logger = logging.getLogger(__name__)

# Put chroma DB inside the vector_db folder locally
CHROMA_DB_DIR = BASE_DIR / "vector_db" / ".chroma"
CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)

class LocalChromaStore:
    def __init__(self):
        try:
            if chromadb is None:
                raise ImportError("chromadb is not installed (likely missing C++ build tools)")
            self.client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
            # Use L2 distance by default, or cosine if specified
            self.collection = self.client.get_or_create_collection(
                name=VECTOR_INDEX_NAME,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("Initialized local ChromaDB successfully.")
        except Exception as e:
            logger.warning(f"Failed to initialize ChromaDB (This is optional for testing): {e}")
            self.collection = None

    def upsert_chunks(self, chunk_ids: List[str], embeddings: List[List[float]], texts: List[str], metadatas: List[Dict[str, Any]]):
        if not self.collection:
            return
            
        try:
            self.collection.add(
                ids=chunk_ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )
        except Exception as e:
            logger.error(f"Failed to upsert to Chroma: {e}")

    def query_similar(self, query_embedding: List[float], top_k: int = 3) -> Dict[str, Any]:
        if not self.collection:
            return {}
            
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            return results
        except Exception as e:
            logger.error(f"Failed to query Chroma: {e}")
            return {}

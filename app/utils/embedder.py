from sentence_transformers import SentenceTransformer
from app.core.logger import logger
from typing import List, Optional

class Embedder:
    _instance: Optional['Embedder'] = None
    model: SentenceTransformer

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Embedder, cls).__new__(cls)
            cls._instance.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("SentenceTransformer model 'all-MiniLM-L6-v2' loaded successfully.")
        return cls._instance


    def embed_document(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()

    def embed_query(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts).tolist()

embedder = Embedder()

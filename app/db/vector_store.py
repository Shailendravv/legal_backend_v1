import chromadb
from app.core.config import settings
from app.core.logger import logger
from typing import List, Dict, Optional, Any

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        self.collection: Any = self.client.get_or_create_collection(name="legal_docs")
        logger.info(f"Connected to ChromaDB at {settings.CHROMA_PERSIST_DIR}")


    def upsert_chunk(self, id: str, content: str, embedding: List[float], metadata: Dict):
        """
        Inserts or updates a legal document chunk with its vector embedding.
        """
        try:
            self.collection.upsert(
                ids=[id],
                documents=[content],
                embeddings=[embedding],
                metadatas=[metadata]
            )
            logger.debug(f"Upserted chunk {id}")
        except Exception as e:
            logger.error(f"Error upserting chunk {id}: {str(e)}")

    def query_similar(self, query_embedding: List[float], n_results: int = 5, where: Optional[Dict] = None) -> List[Dict]:
        """
        Retrieves top n similar document chunks for a given query embedding.
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where
            )
            
            # Format results into a cleaner list of dicts
            formatted_results = []
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i]
                })
            
            return formatted_results
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {str(e)}")
            return []

    def get_all_documents(self) -> List[str]:
        """
        Fetches all stored document texts for in-memory BM25 index building.
        """
        try:
            results = self.collection.get()
            return results['documents']
        except Exception as e:
            logger.error(f"Error fetching all documents: {str(e)}")
            return []

vector_store = VectorStore()


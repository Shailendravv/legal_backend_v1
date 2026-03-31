from rank_bm25 import BM25Okapi
from typing import List, Dict
from app.core.logger import logger

class BM25Index:
    def __init__(self):
        self.index = None
        self.documents = []

    def build_index(self, documents: List[str]):
        """
        Builds the BM25 index from a list of document strings.
        Each document is tokenized by splitting on whitespace.
        """
        if not documents:
            logger.warning("Empty document list provided for BM25 indexing.")
            return

        self.documents = documents
        tokenized_corpus = [doc.lower().split() for doc in documents]
        self.index = BM25Okapi(tokenized_corpus)
        logger.info(f"BM25 index built with {len(documents)} documents.")

    def search(self, query: str, n: int = 5) -> List[Dict]:
        """
        Performs a keyword search and returns top n results with their original content and scores.
        """
        if self.index is None:
            logger.error("BM25 index not built yet.")
            return []

        tokenized_query = query.lower().split()
        scores = self.index.get_scores(tokenized_query)
        doc_scores = list(zip(self.documents, scores))
        # Sort by score in descending order
        sorted_results = sorted(doc_scores, key=lambda x: x[1], reverse=True)[:n]
        
        return [{"content": res[0], "score": res[1]} for res in sorted_results]

bm25_index = BM25Index()

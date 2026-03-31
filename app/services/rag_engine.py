from loguru import logger
from app.db.vector_store import vector_store
from app.services.groq_client import groq_client
from app.utils.embedder import embedder
from app.utils.bm25_index import bm25_index
from app.utils.rrf import merge_results
from app.utils.prompt_builder import build_system_prompt, build_context, build_messages
from typing import List, Dict, AsyncGenerator, Optional

class RAGEngine:
    def __init__(self):
        # Build BM25 index on initialization
        self.refresh_bm25_index()

    def refresh_bm25_index(self):
        """
        Reloads all documents from ChromaDB and rebuilds the BM25 index.
        """
        logger.info("Initializing BM25 index from vector store documents...")
        all_docs = vector_store.get_all_documents()
        bm25_index.build_index(all_docs)

    async def retrieve_and_generate(self, user_query: str, history: List[Dict] = []) -> AsyncGenerator[str, None]:
        """
        Retrieves relevant legal context using a hybrid (vector + keyword) approach
        and returns an asynchronous stream of response tokens from Groq.
        """
        logger.info(f"Processing hybrid retrieval for query: {user_query}")
        
        # 1. Vector Search
        query_embedding = embedder.embed_query(user_query)
        vector_results = vector_store.query_similar(query_embedding, n_results=5)

        # 2. Keyword (BM25) Search
        bm25_results = bm25_index.search(user_query, n=5)

        # 3. Hybrid Reranking (RRF)
        fused_results = merge_results(vector_results, bm25_results, n=5)

        # 4. Context & Prompt Assembly
        context_str = build_context(fused_results)
        system_prompt = build_system_prompt()
        messages = build_messages(system_prompt, context_str, history, user_query)

        # 5. Groq Streaming Completion
        async for token in groq_client.stream_completion(messages):
            yield token

rag_engine = RAGEngine()


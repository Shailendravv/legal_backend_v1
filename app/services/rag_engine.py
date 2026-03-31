from loguru import logger
from app.db.vector_store import vector_store
from app.services.groq_client import groq_client

class RAGEngine:
    def get_context(self, query: str):
        logger.debug(f"Retrieving context for query: {query}")
        results = vector_store.query(query_texts=[query])
        context = "\n".join(results['documents'][0])
        logger.debug(f"Retrieved {len(results['documents'][0])} documents")
        return context

    def query(self, user_query: str):
        logger.info(f"Processing query: {user_query}")
        context = self.get_context(user_query)
        prompt = f"Context: {context}\n\nQuestion: {user_query}\n\nAnswer based on context:"
        response = groq_client.generate_response(prompt)
        logger.info("Query processing complete")
        return response

rag_engine = RAGEngine()

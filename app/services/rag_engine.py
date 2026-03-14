from app.db.vector_store import vector_store
from app.services.groq_client import groq_client

class RAGEngine:
    def get_context(self, query: str):
        results = vector_store.query(query_texts=[query])
        return "\n".join(results['documents'][0])

    def query(self, user_query: str):
        context = self.get_context(user_query)
        prompt = f"Context: {context}\n\nQuestion: {user_query}\n\nAnswer based on context:"
        return groq_client.generate_response(prompt)

rag_engine = RAGEngine()

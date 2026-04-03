from app.utils.bm25_index import bm25_index
from app.utils.rrf import merge_results

def test_hybrid_logic():
    # Mock documents for testing
    docs = [
        "The Supreme Court of India is the highest judicial court.",
        "Legal procedures for criminal cases involve evidence gathering.",
        "Constitutional law defines the powers of the government.",
        "Indian penal code deals with criminal offenses.",
    ]
    
    print("\n--- Testing BM25 Indexing ---")
    bm25_index.build_index(docs)
    
    query = "criminal justice in India"
    print(f"Query: {query}")
    
    # 1. Test Keyword Search
    bm25_results = bm25_index.search(query, n=3)
    print("\nBM25 Results:")
    for i, res in enumerate(bm25_results, 1):
        print(f"{i}. Score: {res['score']:.4f} | Content: {res['content'][:50]}...")

    # 2. Mock Vector Search Results (similar format)
    # Usually vector search returns distances or similar scores.
    # In rrf.py: merge_results(vector_results, bm25_results)
    vector_results = [
        {"content": docs[1], "metadata": {"source": "manual"}, "score": 0.9},
        {"content": docs[3], "metadata": {"source": "manual"}, "score": 0.8},
    ]
    
    print("\nMock Vector Results:")
    for i, res in enumerate(vector_results, 1):
        print(f"{i}. Score: {res['score']:.4f} | Content: {res['content'][:50]}...")

    # 3. Test RRF Fusion
    print("\n--- Testing RRF Fusion ---")
    fused_results = merge_results(vector_results, bm25_results, n=3)
    
    print("\nFused Results (Reciprocal Rank Fusion):")
    for i, res in enumerate(fused_results, 1):
        print(f"{i}. RRF Score: {res['rrf_score']:.4f} | Content: {res['content'][:50]}...")

if __name__ == "__main__":
    test_hybrid_logic()

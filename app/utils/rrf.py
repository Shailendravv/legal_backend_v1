from typing import List, Dict
from collections import defaultdict
from app.core.logger import logger

def merge_results(vector_results: List[Dict], bm25_results: List[Dict], n: int = 5, k: int = 60) -> List[Dict]:
    """
    Reciprocal Rank Fusion (RRF) to merge and re-rank vector and keyword search results.
    RRF score = sum(1 / (k + rank_i))
    """
    scores = defaultdict(float)
    content_map = {}

    # Rank vector results
    for rank, res in enumerate(vector_results, 1):
        content = res['content']
        scores[content] += 1 / (k + rank)
        content_map[content] = res.get('metadata', {})

    # Rank BM25 results
    for rank, res in enumerate(bm25_results, 1):
        content = res['content']
        scores[content] += 1 / (k + rank)
        if content not in content_map:
            content_map[content] = res.get('metadata', {})

    # Sort content by fusion score in descending order
    sorted_content = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    top_n_results = []
    for content, score in sorted_content[:n]:
        top_n_results.append({
            "content": content,
            "metadata": content_map.get(content, {}),
            "rrf_score": score
        })

    logger.debug(f"Merged {len(vector_results)} vector and {len(bm25_results)} BM25 results using RRF.")
    return top_n_results

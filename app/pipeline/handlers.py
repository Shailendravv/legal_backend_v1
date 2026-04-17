import os
from typing import Any, Dict, Optional
from app.core.logger import logger

class BaseHandler:
    """Base class for source handlers."""
    async def fetch(self, source: str) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement fetch()")

class LocalFileHandler(BaseHandler):
    """Handles loading content from local file system."""
    
    async def fetch(self, source: str) -> Dict[str, Any]:
        logger.info(f"[LOCAL_HANDLER] Fetching: {source}")
        
        if not os.path.exists(source):
            raise FileNotFoundError(f"Local file not found: {source}")
        
        file_ext = os.path.splitext(source)[1].lower()
        
        # For binary files (PDF, Parquet, CSV), we pass the path to the extractor
        # For text files, we might read the content? 
        # Actually, the extractor is already designed to take paths for PDF/CSV/Parquet.
        
        source_type = "text"
        if file_ext == ".pdf":
            source_type = "pdf"
        elif file_ext == ".csv":
            source_type = "csv"
        elif file_ext == ".parquet":
            source_type = "parquet"
        elif file_ext in [".txt", ".md"]:
            source_type = "text"
            with open(source, 'r', encoding='utf-8') as f:
                content = f.read()
                return {
                    "content": content,
                    "source_type": source_type,
                    "metadata": {"path": source, "size": os.path.getsize(source)}
                }
        
        # Default for structured files: pass the path as content
        return {
            "content": source,
            "source_type": source_type,
            "metadata": {"path": source, "size": os.path.getsize(source)}
        }

class HuggingFaceHandler(BaseHandler):
    """Handles loading datasets from Hugging Face."""
    
    async def fetch(self, source: str) -> Dict[str, Any]:
        # source format expected: hf:repo_id/dataset_name/subset
        logger.info(f"[HF_HANDLER] Fetching: {source}")
        
        try:
            from datasets import load_dataset
            
            # Strip 'hf:' prefix
            dataset_path = source[3:] if source.lower().startswith("hf:") else source
            
            # Parse for query parameters (e.g. hf:repo/name?q=keyword)
            search_query = None
            if "?" in dataset_path:
                dataset_path, params = dataset_path.split("?", 1)
                for param in params.split("&"):
                    if param.startswith("q=") or param.startswith("query="):
                        search_query = param.split("=", 1)[1].replace("+", " ").lower()
            
            # Split path and subset if provided
            parts = dataset_path.split("/")
            repo_id = "/".join(parts[:2])
            subset = parts[2] if len(parts) > 2 else None
            
            logger.info(f"[HF_HANDLER] Loading dataset: {repo_id}, subset: {subset}, search: {search_query}")
            
            # --- New Approach: Use Hugging Face Search API if query exists ---
            if search_query:
                try:
                    import httpx
                    search_url = "https://datasets-server.huggingface.co/search"
                    query_params = {
                        "dataset": repo_id,
                        "config": subset or "default",
                        "split": "train",
                        "query": search_query
                    }
                    logger.info(f"[HF_HANDLER] Calling Search API: {search_url} with params {query_params}")
                    
                    async with httpx.AsyncClient() as client:
                        response = await client.get(search_url, params=query_params, timeout=100.0)
                        if response.status_code == 200:
                            data = response.json()
                            rows = [item["row"] for item in data.get("rows", [])]
                            logger.info(f"[HF_HANDLER] Search API success: Found {len(rows)} matching rows.")
                            return {
                                "content": rows,
                                "source_type": "csv",
                                "metadata": {
                                    "repo": repo_id,
                                    "subset": subset,
                                    "search_query": search_query,
                                    "count": len(rows),
                                    "note": f"Found {len(rows)} matches via Search API"
                                }
                            }
                        else:
                            logger.warning(f"[HF_HANDLER] Search API returned status {response.status_code}. Falling back to stream.")
                except Exception as e:
                    logger.error(f"[HF_HANDLER] Search API failed ({type(e).__name__}): {str(e)}. Falling back to stream.")

            # --- Fallback: Sequential Streaming ---
            logger.info(f"[HF_HANDLER] Initializing fallback stream for {repo_id}")
            ds = load_dataset(repo_id, subset, split='train', streaming=True)
            
            examples = []
            it = iter(ds)
            max_rows = 5 if not search_query else 10 
            
            # Increase scan range for better coverage on large datasets
            scan_limit = 5000 if search_query else 1000
            
            for _ in range(scan_limit): 
                try:
                    row = next(it)
                    # Case-insensitive search across all values in the row
                    if not search_query or any(search_query in str(v).lower() for v in row.values()):
                        examples.append(row)
                        if len(examples) >= max_rows:
                            break
                except StopIteration:
                    break
            
            return {
                "content": examples,
                "source_type": "csv",
                "metadata": {
                    "repo": repo_id,
                    "subset": subset,
                    "search_query": search_query,
                    "count": len(examples),
                    "note": f"Top {len(examples)} matches (Stream/Fallback | Scan: {scan_limit})"
                }
            }
        except ImportError:
            logger.error("[HF_HANDLER] 'datasets' library not installed")
            raise
        except Exception as e:
            logger.error(f"[HF_HANDLER] Error: {str(e)}")
            raise

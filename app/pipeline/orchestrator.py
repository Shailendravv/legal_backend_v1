import os
from typing import Any, Dict
from app.core.logger import logger
from app.crawler.playwright_crawler import PlaywrightCrawler
from app.pipeline.handlers import LocalFileHandler, HuggingFaceHandler

class SourceOrchestrator:
    """
    Decouples the data source from the processing pipeline.
    Determines whether to use a crawler, local file handler, or dataset loader.
    """
    
    def __init__(self):
        self.crawler = PlaywrightCrawler()
        # Other handlers will be initialized here as implemented
        self.hf_handler = HuggingFaceHandler()
        self.local_handler = LocalFileHandler()

    async def route_and_fetch(self, source: str) -> Dict[str, Any]:
        """
        Routes the source string to the appropriate handler and returns content.
        """
        logger.info(f"[ORCHESTRATOR] Routing source: {source}")
        
        # 1. Web Source
        if source.startswith("http"):
            logger.info("[ORCHESTRATOR] Strategy: Web Crawler")
            crawl_result = await self.crawler.dynamic_crawl(source)
            return {
                "source": source,
                "strategy": f"WebCrawler ({crawl_result['strategy']})",
                "source_type": "html",
                "content": crawl_result["content"],
                "metadata": {
                    "parsed_act": crawl_result.get("parsed_act"),
                    "parsed_section": crawl_result.get("parsed_section"),
                    "status": "success"
                }
            }
        
        # 2. Hugging Face Source
        elif source.startswith("HF:") or source.startswith("hf:"):
            logger.info("[ORCHESTRATOR] Strategy: HuggingFace Dataset")
            hf_result = await self.hf_handler.fetch(source)
            return {
                "source": source,
                "strategy": "HuggingFace",
                "source_type": hf_result["source_type"],
                "content": hf_result["content"],
                "metadata": hf_result["metadata"]
            }
            
        # 3. Local File Source
        elif source.endswith((".pdf", ".parquet", ".csv", ".txt", ".md")) or os.path.isabs(source):
            # Also check if it's a file path even if no standard extension
            if os.path.exists(source) or source.endswith((".pdf", ".parquet", ".csv", ".txt", ".md")):
                logger.info("[ORCHESTRATOR] Strategy: Local File")
                local_result = await self.local_handler.fetch(source)
                return {
                    "source": source,
                    "strategy": "LocalFile",
                    "source_type": local_result["source_type"],
                    "content": local_result["content"],
                    "metadata": local_result["metadata"]
                }
            
        # 4. Search Query Fallback
        logger.info("[ORCHESTRATOR] Strategy: Query-to-Search (Playwright)")
        crawl_result = await self.crawler.dynamic_crawl(source)
        return {
            "source": source,
            "strategy": f"SearchCrawler ({crawl_result['strategy']})",
            "source_type": "text",
            "content": crawl_result["content"],
            "metadata": {
                "parsed_act": crawl_result.get("parsed_act"),
                "parsed_section": crawl_result.get("parsed_section"),
                "status": "success"
            }
        }

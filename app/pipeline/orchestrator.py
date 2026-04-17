from typing import Any, Dict
from app.core.logger import logger
from app.crawler.playwright_crawler import PlaywrightCrawler

class SourceOrchestrator:
    """
    Decouples the data source from the processing pipeline.
    Determines whether to use a crawler, local file handler, or dataset loader.
    """
    
    def __init__(self):
        self.crawler = PlaywrightCrawler()
        # Other handlers will be initialized here as implemented
        # self.hf_handler = HuggingFaceHandler()
        # self.local_handler = LocalFileHandler()

    async def route_and_fetch(self, source: str) -> Dict[str, Any]:
        """
        Routes the source string to the appropriate handler and returns content.
        """
        logger.info(f"[ORCHESTRATOR] Routing source: {source}")
        
        if source.startswith("http"):
            logger.info("[ORCHESTRATOR] Strategy: Web Crawler")
            crawl_result = await self.crawler.dynamic_crawl(source)
            return {
                "source": source,
                "strategy": f"WebCrawler ({crawl_result['strategy']})",
                "content": crawl_result["content"],
                "metadata": {
                    "parsed_act": crawl_result.get("parsed_act"),
                    "parsed_section": crawl_result.get("parsed_section"),
                    "status": "success"
                }
            }
        
        elif source.startswith("HF:") or source.startswith("hf:"):
            logger.info("[ORCHESTRATOR] Strategy: HuggingFace Dataset (Mocked)")
            # Mocking HF for now as per Step 3 report gaps
            return {
                "source": source,
                "strategy": "HuggingFace",
                "content": "Sample content from HuggingFace dataset.",
                "metadata": {"status": "mocked"}
            }
            
        elif source.endswith((".pdf", ".parquet", ".csv")):
            logger.info("[ORCHESTRATOR] Strategy: Structured/Static File (Mocked)")
            return {
                "source": source,
                "strategy": "LocalFile",
                "content": f"Sample binary content from {source}",
                "metadata": {"status": "mocked"}
            }
            
        else:
            # Fallback for plain text queries (treated as search)
            logger.info("[ORCHESTRATOR] Strategy: Query-to-Search (Playwright)")
            crawl_result = await self.crawler.dynamic_crawl(source)
            return {
                "source": source,
                "strategy": f"SearchCrawler ({crawl_result['strategy']})",
                "content": crawl_result["content"],
                "metadata": {
                    "parsed_act": crawl_result.get("parsed_act"),
                    "parsed_section": crawl_result.get("parsed_section"),
                    "status": "success"
                }
            }

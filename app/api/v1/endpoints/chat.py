from fastapi import APIRouter
from app.core.logger import logger
from app.crawler.playwright_crawler import PlaywrightCrawler

router = APIRouter()

@router.post("/chat")
async def chat_interaction():
    # TEST: Step 1 Implementation verification
    logger.info("Chat interaction hijacking for Step 1 (Crawler) Verification")
    
    # test_url = "https://example.com"
    # test_url = "https://indiankanoon.org/doc/1070476/"
    test_url = "https://www.wikipedia.org/"
    crawler = PlaywrightCrawler()
    
    # Execute the crawler (Step 1)
    raw_content = await crawler.crawl(test_url)
    
    return {
        "step": "1",
        "description": "Data Ingestion Pipeline: Playwright Crawler",
        "status": "SUCCESS",
        "input_url": test_url,
        "raw_content_length": len(raw_content),
        "logs": [
            "[START] Step 1: Playwright Crawler - Fetching...",
            f"[END] Step 1: Playwright Crawler - Fetched {len(raw_content)} chars."
        ]
    }

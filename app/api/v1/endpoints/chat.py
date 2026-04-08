from fastapi import APIRouter
from app.core.logger import logger
from app.crawler.playwright_crawler import PlaywrightCrawler
from app.pipeline.extractor import ContentExtractor

router = APIRouter()

@router.post("/chat")
async def chat_interaction():
    # Pipeline Step 1 & 2 Verification
    logger.info("Executing Pipeline: Ingestion -> Extraction")
    
    # --- Step 1: Crawler ---
    test_url = "https://www.wikipedia.org/"
    crawler = PlaywrightCrawler()
    raw_content = await crawler.crawl(test_url)
    
    # --- Step 2: Content Extractor ---
    extractor = ContentExtractor()
    extraction_input = {
        "source_type": "html",
        "content": raw_content
    }
    
    extraction_output = await extractor.run(extraction_input)
    
    # Return formatted response as requested
    return {
        "current_step": "Content Extractor",
        "input_type": extraction_output.get("input_type"),
        "status": extraction_output.get("status"),
        "output_preview": extraction_output.get("extracted_content")[:500] if isinstance(extraction_output.get("extracted_content"), str) else str(extraction_output.get("extracted_content")[:5]),
        "next_step": "Cleaner (pending)"
    }

from fastapi import APIRouter
from app.core.logger import logger
from app.crawler.playwright_crawler import PlaywrightCrawler
from app.pipeline.extractor import ContentExtractor
from app.pipeline.cleaner import ContentCleaner

router = APIRouter()

@router.post("/chat")
async def chat_interaction():
    # Pipeline Step 1, 2 & 3 Verification
    logger.info("Executing Pipeline: Ingestion -> Extraction -> Cleaning")
    
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
    
    # --- Step 3: Cleaner ---
    cleaner = ContentCleaner()
    cleaning_input = {
        "type": "html",
        "data": extraction_output.get("extracted_content")
    }
    cleaning_output = await cleaner.run(cleaning_input)
    
    # Return formatted response as requested
    return {
        "current_step": "Cleaner",
        "input_type": cleaning_output.get("input_type"),
        "status": cleaning_output.get("status"),
        "output_preview": cleaning_output.get("output_preview"),
        "pii_flags": cleaning_output.get("pii_flags"),
        "next_step": "Section Chunker (pending)"
    }

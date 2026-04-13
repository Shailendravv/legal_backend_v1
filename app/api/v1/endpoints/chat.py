from fastapi import APIRouter
from pydantic import BaseModel
from app.core.logger import logger
from app.crawler.playwright_crawler import PlaywrightCrawler
from app.pipeline.extractor import ContentExtractor
from app.pipeline.cleaner import ContentCleaner

router = APIRouter()

class ChatRequest(BaseModel):
    user_query: str

@router.post("/chat")
async def chat_interaction(request: ChatRequest):
    """
    Takes JSON input from frontend: { "user_query": "IPC 420" }
    """
    user_query = request.user_query
    # Pipeline Step 1, 2 & 3 Verification with Dynamic Search
    logger.info(f"Executing Dynamic Pipeline for query: {user_query}")
    
    # --- Step 1: Dynamic Crawler ---
    crawler = PlaywrightCrawler()
    crawl_result = await crawler.dynamic_crawl(user_query)
    raw_content = crawl_result["content"]
    
    # --- Step 2: Content Extractor ---
    extractor = ContentExtractor()
    extraction_input = {
        "source_type": "text", # Using text as input from dynamic crawl
        "content": raw_content
    }
    extraction_output = await extractor.run(extraction_input)
    
    # --- Step 3: Cleaner ---
    cleaner = ContentCleaner()
    cleaning_input = {
        "type": "text",
        "data": extraction_output.get("extracted_content")
    }
    cleaning_output = await cleaner.run(cleaning_input)
    
    # Return formatted response as requested
    return {
        "current_step": "Cleaner",
        "query": user_query,
        "resolved_act": crawl_result["parsed_act"],
        "resolved_section": crawl_result["parsed_section"],
        "ingestion_strategy": f"Dynamic ({crawl_result['strategy']})",
        "input_type": cleaning_output.get("input_type"),
        "status": cleaning_output.get("status"),
        "output_preview": cleaning_output.get("output_preview"),
        "pii_flags": cleaning_output.get("pii_flags"),
        "next_step": "Section Chunker (pending)"
    }

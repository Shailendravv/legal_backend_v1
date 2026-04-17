from fastapi import APIRouter
from pydantic import BaseModel
from app.core.logger import logger
from app.pipeline.orchestrator import SourceOrchestrator
from app.pipeline.extractor import ContentExtractor
from app.pipeline.cleaner import ContentCleaner

router = APIRouter()

class ChatRequest(BaseModel):
    user_query: str

@router.post("/chat")
async def chat_interaction(request: ChatRequest):
    """
    Unified Ingestion API: Orchestrates Source -> Extraction -> Cleaning
    """
    user_query = request.user_query
    logger.info(f"🚀 [UNIFIED PIPELINE] Internalizing query: {user_query}")
    
    # --- Step 1: Source Orchestrator (The Inlet) ---
    orchestrator = SourceOrchestrator()
    source_result = await orchestrator.route_and_fetch(user_query)
    
    # --- Step 2: Content Extractor ---
    extractor = ContentExtractor()
    extraction_input = {
        "source_type": source_result.get("source_type", "html"),
        "content": source_result["content"]
    }
    extraction_output = await extractor.run(extraction_input)
    
    # --- Step 3: Cleaner ---
    if extraction_output.get("status") == "completed" and extraction_output.get("extracted_content"):
        cleaner = ContentCleaner()
        cleaning_input = {
            "type": extraction_output.get("input_type", "text"),
            "data": extraction_output.get("extracted_content")
        }
        cleaning_output = await cleaner.run(cleaning_input)
    else:
        # Fallback for empty or failed extraction
        cleaning_output = {
            "current_step": "Cleaner",
            "status": "skipped",
            "reason": "No content extracted to clean"
        }
    
    # --- Return Detailed Debug Response ---
    return {
        "pipeline_metadata": {
            "query": user_query,
            "orchestrator_strategy": source_result["strategy"],
            "source_resolved": source_result["source"],
            "status": "success" if cleaning_output.get("status") == "completed" else "partial_failure"
        },
        "legal_context": {
            "resolved_act": source_result["metadata"].get("parsed_act"),
            "resolved_section": source_result["metadata"].get("parsed_section"),
            "source_reliability": "high" if "direct_url" in source_result["strategy"] else "medium"
        },
        "processing_stages": {
            "extraction": {
                "input_type": extraction_output.get("input_type"),
                "status": extraction_output.get("status")
            },
            "cleaning": {
                "pii_detected": cleaning_output.get("pii_flags", {}).get("pii_found", False),
                "anonymization": "applied" if cleaning_output.get("pii_flags", {}).get("pii_found", False) else "none"
            }
        },
        "output": {
            "preview": cleaning_output.get("output_preview"),
            "full_content_length": len(cleaning_output.get("output_preview", "")) if cleaning_output.get("output_preview") else 0,
            "next_steps": ["Semantic Chunking", "Embedding Generation", "Qdrant Upsert"]
        }
    }

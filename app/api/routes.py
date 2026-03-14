from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from loguru import logger
from app.services.rag_engine import rag_engine

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@router.get("/health")
async def health_check():
    logger.info("Health check endpoint called")
    return {"status": "healthy"}

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    logger.info(f"Received chat request: {request.message[:50]}...")
    try:
        response = rag_engine.query(request.message)
        logger.info("Successfully generated response")
        return ChatResponse(response=response)
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

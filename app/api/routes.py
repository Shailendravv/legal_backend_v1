from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag_engine import rag_engine

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = rag_engine.query(request.message)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.core.logger import logger
from app.services.rag_engine import rag_engine
from app.db.session_store import session_store
import json

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: str

@router.get("/health")
async def health_check():
    logger.info("Health check endpoint called")
    return {"status": "healthy"}

@router.post("/chat")
async def chat(request: ChatRequest):
    logger.info(f"Received streaming chat request for session {request.session_id}")
    
    async def event_generator():
        full_response = ""
        try:
            # Get history from session store
            history_turns = session_store.get_history(request.session_id)
            history_dicts = [{"role": t.role, "content": t.content} for t in history_turns]

            # Stream from RAG Engine
            async for token in rag_engine.retrieve_and_generate(request.message, history_dicts):
                full_response += token
                # Format as SSE (Server-Sent Events) compatible or just raw tokens
                # folder-structure.md mentions "data: {token}" format for SSE
                yield f"data: {json.dumps({'token': token})}\n\n"
            
            # Save the turn after completion
            session_store.save_turn(request.session_id, "user", request.message)
            session_store.save_turn(request.session_id, "assistant", full_response)
            
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"Error in event_generator: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/history/{session_id}")
async def get_history(session_id: str):
    history = session_store.get_history(session_id)
    return {"history": history}

@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    session_store.delete_session(session_id)
    return {"status": "cleared"}


from fastapi import APIRouter
from app.core.logger import logger

router = APIRouter()

@router.post("/chat")
async def chat_interaction():
    logger.info("Chat interaction initiated")
    return {"message": "Chat service initialized"}

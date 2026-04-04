from fastapi import APIRouter
from app.api.v1.endpoints import chat, pipeline, health

router = APIRouter()

router.include_router(chat.router, tags=["Chat"])
router.include_router(pipeline.router, tags=["Pipeline"])
router.include_router(health.router, tags=["System"])

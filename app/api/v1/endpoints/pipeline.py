from fastapi import APIRouter
from app.core.logger import logger

router = APIRouter()

@router.post("/pipeline/start")
async def start_pipeline():
    logger.info("Pipeline execution started via API")
    return {"status": "started", "pipeline_id": "test-pipeline-001"}

@router.get("/pipeline/status/{pipeline_id}")
async def get_pipeline_status(pipeline_id: str):
    logger.info(f"Querying status for pipeline: {pipeline_id}")
    return {"pipeline_id": pipeline_id, "status": "running"}

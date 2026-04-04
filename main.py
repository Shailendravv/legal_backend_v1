import uvicorn
from fastapi import FastAPI
from app.core.logger import setup_logger
from app.api.v1.router import router as api_router

# Initialize Logger
setup_logger()

app = FastAPI(title="Legal AI RAG Backend")

# Include API routes
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
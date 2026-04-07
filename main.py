import asyncio
import sys
import uvicorn
from fastapi import FastAPI
from app.core.logger import setup_logger
from app.api.v1.router import router as api_router

# Fix for Windows: Playwright requires ProactorEventLoop to support subprocesses
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Initialize Logger
setup_logger()

app = FastAPI(title="Legal AI RAG Backend")

# Include API routes
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
import uvicorn
from fastapi import FastAPI
from app.api.routes import router
from app.core.logger import setup_logger

# Initialize Logger
setup_logger()

app = FastAPI(title="Legal AI RAG Backend")

app.include_router(router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

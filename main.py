import uvicorn
from fastapi import FastAPI
from app.core.logger import setup_logger

# Initialize Logger
setup_logger()

app = FastAPI(title="Legal AI RAG Backend")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
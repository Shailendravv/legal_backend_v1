import uvicorn
from fastapi import FastAPI

app = FastAPI(title="Legal AI RAG Backend")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
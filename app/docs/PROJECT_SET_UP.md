# Legal Project Backend Setup Documentation

This document outlines the structure, setup process, and basic operations for the Legal RAG (Retrieval-Augmented Generation) backend.

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9+
- [Groq API Key](https://console.groq.com/keys)

### 2. Installation
Clone the repository and install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory (one is already provided as a template) and add your Groq API key:
```env
GROQ_API_KEY=your_groq_api_key_here
CHROMA_DB_PATH=./chroma_db
```

### 4. Running the Server
Run the FastAPI application using Uvicorn:
```bash
python main.py
```
The server will start at `http://0.0.0.0:8000`.

## 📁 Project Structure

```text
backend/
├── app/
│   ├── api/
│   │   └── routes.py          # Chat & Health check endpoints
│   ├── core/
│   │   └── config.py          # Environment variables & Pydantic settings
│   ├── db/
│   │   └── vector_store.py    # ChromaDB initialization & operations
│   ├── docs/
│   │   └── PROJECT_SET_UP.md  # This documentation file
│   └── services/
│       ├── groq_client.py     # Wrapper for Groq's LLM API
│       └── rag_engine.py      # Logic for Retrieval-Augmented Generation
├── .env                       # Environment variables (do not commit secrets)
├── main.py                    # Entry point for the FastAPI application
└── requirements.txt           # Python dependencies
```

## 🛠️ API Endpoints

### Health Check
- **URL**: `/api/health`
- **Method**: `GET`
- **Description**: Verifies if the server is running.

### Chat (RAG)
- **URL**: `/api/chat`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "message": "Enter your legal query here"
  }
  ```
- **Description**: Queries the vector store for relevant context and generates a response using Groq's LLM.

## 📝 Notes
- **ChromaDB**: The vector store is persisted in the path specified by `CHROMA_DB_PATH`.
- **LLM Model**: Currently defaults to `llama-3.3-70b-versatile` via Groq.

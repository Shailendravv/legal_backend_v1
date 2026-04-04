# Backend Setup Guide

This document provides a comprehensive guide to setting up, developing, and deploying the **Legal AI Backend** service.

## 📁 Project Structure

Our project follows a modular and scalable structure designed for enterprise-grade FastAPI applications. This ensures clean separation of concerns and high maintainability.

```text
backend/
├── app/
│   ├── api/                # API Route handlers
│   │   └── v1/             # Versioning: API v1
│   │       ├── endpoints/  # Specific route controllers (chat, docs)
│   │       └── router.py   # Aggregated APIv1 router
│   ├── core/               # Core application logic & config
│   │   ├── config.py       # Pydantic settings management
│   │   ├── security.py     # JWT & Authentication logic
│   │   └── logger.py       # Standardized structured logging
│   ├── db/                 # Database & Vector Store integrations
│   │   └── vector_store.py # ChromaDB/Pinecone/PGVector logic
│   ├── models/             # Database/Table models (SQLAlchemy/Tortoise)
│   ├── schemas/            # Pydantic models for request/response validation
│   ├── services/           # Business logic (RAG engine, LLM API calls)
│   │   ├── rag_engine.py   # Context retrieval and processing
│   │   └── llm_client.py   # Client for OpenAI/Claude/Local LLMs
│   └── main.py             # FastAPI entry point
├── tests/                  # Integration and unit tests
├── logs/                   # Application log files
├── .env                    # Environment variables (Private)
├── .env.example            # Environment variables template
├── pyproject.toml          # Project metadata and dependencies
└── setup.md                # Project setup and documentation (This file)
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (Fastest Python package manager)
- Docker (Optional, for containerized database services)

### 2. Environment Setup
Clone the repository and initialize the virtual environment:

```bash
# Initialize venv using uv
uv venv

# Activate the environment
# On Windows:
.venv\Scripts\activate
# On Linux/MacOS:
source .venv/bin/activate

# Install dependencies
uv sync
```

### 3. Configuration
Copy the `.env.example` file to `.env` and fill in the required credentials:

```bash
cp .env.example .env
```

| Key | Description | Default |
|-----|-------------|---------|
| `DATABASE_URL` | PostgreSQL or Vector DB URI | `sqlite:///./test.db` |
| `OPENAI_API_KEY` | Key for LLM Processing | `Required` |
| `LOG_LEVEL` | Logging verbosity (DEBUG/INFO/ERROR) | `INFO` |

### 4. Running the Application
Start the development server with hot-reload enabled:

```bash
uv run uvicorn main:app --reload
```

The API will be available at: [http://localhost:8000](http://localhost:8000)
Interactive API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📡 API Endpoints (v1)

All endpoints below are prefixed with `/api/v1`.

### 🩺 System
- `GET /health`: Check if the service is running.

### 💬 Chat & AI
- `POST /chat`: Main endpoint for legal consultation queries. Integrates RAG and LLM.
- `GET /chat/history`: Fetch conversation history for a specific user session.

### 📄 Document Management
- `POST /documents/upload`: Upload PDF/TXT files for vector indexing.
- `GET /documents/list`: Retrieve a list of processed legal documents.
- `DELETE /documents/{id}`: Remove a document from the vector store.

### 👤 Authentication
- `POST /auth/login`: Generate JWT access tokens.
- `POST /auth/register`: Create new user accounts if applicable.

---

## 🛠 Advanced Usage

### Running Tests
We use `pytest` for testing. Run all tests with:
```bash
uv run pytest
```

### Linting & Formatting
Ensure code quality using `ruff`:
```bash
uv run ruff check .
uv run ruff format .
```

### Docker Support
Build the container image:
```bash
docker build -t legal-backend .
```

---

## 📝 Best Practices
1. **Pydantic Schemas**: Always define request/response schemas in `app/schemas/`. Do not return raw DB models.
2. **Dependency Injection**: Use FastAPI's `Depends` for handling DB sessions and service instances.
3. **Structured Logging**: Use the logger found in `app.core.logger` for all server logs.
4. **Environment Variables**: Never hardcode secrets. Use `app/core/config.py`.

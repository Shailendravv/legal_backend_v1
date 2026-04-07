# Backend Setup Guide

This document provides a comprehensive guide to setting up, developing, and deploying the **Legal AI Backend** service.

## 📁 Project Structure

Our project follows a modular and scalable structure designed for enterprise-grade FastAPI applications using a RAG (Retrieval-Augmented Generation) and Agentic patterns.

```text
backend/
├── app/
│   ├── api/                # API Route handlers
│   │   └── v1/             # Versioning: API v1
│   │       ├── endpoints/  # Specific route controllers (chat, ingest, health)
│   │       └── router.py   # Aggregated APIv1 router
│   ├── core/               # Core application logic & config
│   │   ├── config.py       # Pydantic settings (Groq, Qdrant, Supabase)
│   │   ├── logger.py       # Standardized structured logging
│   │   └── pipeline_registry.py # Workflow execution tracking
│   ├── crawler/            # Web crawling & data ingestion module
│   │   ├── base.py         # Abstract crawler interface
│   │   ├── parsers/        # Content-specific parsing logic (Marker/BeautifulSoup)
│   │   └── pipelines/      # Ingestion-stage processing (IPC-BNS mapping)
│   ├── db/                 # Database & Vector Store integrations
│   │   ├── vector_store.py # Qdrant Cloud integration
│   │   └── session_store.py # Supabase PostgreSQL interaction
│   ├── services/           # Orchestration layer (business logic)
│   │   ├── rag_engine.py   # Hybrid search (Dense + Sparse) logic
│   │   └── legal_agent.py  # LangGraph multi-step agent logic
│   ├── schemas/            # Pydantic models for validation
│   └── main.py             # FastAPI entry point
├── tests/                  # Integration and unit tests
├── artifacts/              # Local design and workflow artifacts
├── .env.example            # Environment variables template
├── pyproject.toml          # Project metadata and dependencies (uv)
└── docs/                   # Documentation (Architecture, Setup)
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.11+**
- **[uv](https://docs.astral.sh/uv/)** (Fastest Python package manager)
- **External Accounts** (Free Tiers):
    - [Groq Console](https://console.groq.com/) (LLM Inference)
    - [Qdrant Cloud](https://cloud.qdrant.io/) (Persistent Vector DB)
    - [Supabase](https://supabase.com/) (Session Storage)

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

# Install Playwright browsers (for crawler)
uv run playwright install chromium
```

### 3. Configuration
Copy the `.env.example` file to `.env` and fill in the required credentials:

```bash
cp .env.example .env
```

| Key | Description | Required |
|-----|-------------|----------|
| `GROQ_API_KEY` | Llama 3 70B inference key | Yes |
| `QDRANT_URL` | Qdrant Cloud Cluster URL | Yes |
| `QDRANT_API_KEY` | Qdrant API Key | Yes |
| `SUPABASE_URL` | Supabase Project URL | Yes |
| `SUPABASE_KEY` | Supabase Anon Key | Yes |
| `LOG_LEVEL` | Logging verbosity (DEBUG, INFO) | `INFO` |

### 4. Running the Application
Start the development server with hot-reload enabled:

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at: [http://localhost:8000](http://localhost:8000)
Interactive API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📡 API Endpoints (v1)

All endpoints below are prefixed with `/api/v1`.

### 🩺 System
- `GET /health`: Check service connectivity and diagnostic status.

### 💬 Chat & Legal AI
- `POST /chat`: Primary endpoint for legal interaction. Routes to **RAG Engine** (factual) or **LangGraph Agent** (scenarios).
- `GET /history/{session_id}`: Retrieve session-specific conversation history from Supabase.

### 📄 Ingestion & Crawler
- `POST /ingest`: Trigger the processing of offline data or scrapped legal acts.
- `POST /crawler/ingest`: Trigger the web crawler for real-time legal data sourcing (India Code, Devgan, etc.).

---

## 🛠 Advanced Usage

### Working with the Agent
Our legal agent uses **LangGraph** to handle complex scenarios and multi-act reasoning.
*   **State Management**: Handled in `app.services.legal_agent`.
*   **Custom Nodes**: Add logic nodes in the graph to check for new legal acts or conflict detection.

### Hybrid Search
Retrieval is performed via a combination of:
1.  **Dense Vectors**: BAAI/bge-small-en-v1.5 embeddings for semantic matching.
2.  **Sparse Vectors**: Native Qdrant keyword matching for specific legal section numbers.

### Code Quality
```bash
uv run ruff check .
uv run ruff format .
```

---

## 📝 Best Practices
1. **IPC-BNS Mapping**: When adding new legal data, ensure the `equivalent_section` metadata is populated.
2. **Streaming**: Always use `StreamingResponse` for chat interactions to minimize Time To First Token (TTFT).
3. **Pydantic**: Use schemas for ALL request/response data; never return raw DB objects.
4. **Environment Variables**: Managed strictly via `app.core.config.Settings`.

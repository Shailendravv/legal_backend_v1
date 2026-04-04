# Backend Setup Guide

This document provides a comprehensive guide to setting up, developing, and deploying the **Legal AI Backend** service.

## 📁 Project Structure

Our project follows a modular and scalable structure designed for enterprise-grade FastAPI applications. This ensures clean separation of concerns and high maintainability.

```text
backend/
├── app/
│   ├── api/                # API Route handlers
│   │   └── v1/             # Versioning: API v1
│   │       ├── endpoints/  # Specific route controllers (chat, pipeline, health)
│   │       └── router.py   # Aggregated APIv1 router
│   ├── core/               # Core application logic & config
│   │   ├── config.py       # Pydantic settings management
│   │   ├── logger.py       # Standardized structured logging
│   │   └── pipeline_registry.py # Workflow execution tracking
│   ├── crawler/            # Web crawling & data ingestion module
│   │   ├── base.py         # Abstract crawler interface
│   │   ├── client.py       # HTTP client (httpx)
│   │   ├── parsers/        # Content-specific parsing logic
│   │   └── pipelines/      # Ingestion-stage processing (clean, format)
│   ├── db/                 # Database & Vector Store integrations
│   ├── models/             # Database/Table models
│   ├── pipeline/           # Generic workflow orchestration engine
│   │   ├── base.py         # Pipeline + stage abstraction
│   │   ├── executor.py     # Execution management
│   │   ├── tracker.py      # Real-time progress monitoring
│   │   └── examples/       # Reference pipeline implementations
│   ├── schemas/            # Pydantic models for validation
│   ├── services/           # Orchestration layer (business logic services)
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
- Docker (Optional, for containerized databases)

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
| `LOG_LEVEL` | Logging verbosity | `INFO` |

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
- `GET /health`: Check service connectivity and diagnostic status.

### 💬 Chat & AI
- `POST /chat`: Primary endpoint for legal interaction. Connects to RAG-service and session history.

### ⚙️ Pipelines
- `POST /pipeline/start`: Initialize a predefined workflow (e.g., legal document indexing).
- `GET /pipeline/status/{id}`: Track the progress and real-time execution logs of an active pipeline.

### 📄 Document & Crawler
- `POST /crawler/ingest`: Trigger the web crawler for external legal data sourcing.
- `GET /documents/list`: Retrieve references of processed documents.

---

## 🛠 Advanced Usage

### Working with Pipelines
Our pipeline system allows you to build complex tasks by chaining multiple `Stages`.
*   **Create a custom stage**: Inherit from `app.pipeline.base.Stage`.
*   **Run a pipeline**: Use `app.pipeline.executor.PipelineExecutor`.

### Code Quality
Ensure code quality using `ruff`:
```bash
uv run ruff check .
uv run ruff format .
```

---

## 📝 Best Practices
1. **Abstraction**: Use inherited interfaces from `app.pipeline.base` and `app.crawler.base`.
2. **Registry**: Register new crawlers or workflows in their respective `registry.py` files.
3. **Pydantic**: Use schemas for ALL request/response data; never return raw DB objects.
4. **Environment Variables**: Managed via `app.core.config.settings`.

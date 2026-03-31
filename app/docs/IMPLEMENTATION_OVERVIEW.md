# Technical Implementation Overview: Legal AI RAG Backend

This document provides a detailed overview of the backend features and components implemented for the Indian Legal AI Chatbot.

## 🏗️ Core Architecture (RAG)

We have implemented a **Retrieval-Augmented Generation (RAG)** pipeline designed for legal precision and efficiency.

### 🔍 Hybrid Retrieval System
Instead of simple vector search, we use a hybrid approach:
1.  **Semantic Search (Vector)**: Uses ChromaDB and `sentence-transformers` (`all-MiniLM-L6-v2`) to find documents based on meaning.
2.  **Keyword Search (BM25)**: Uses the `rank-bm25` algorithm for exact term matching (critical for legal terminology like specific Act names or section numbers).
3.  **Reciprocal Rank Fusion (RRF)**: A custom utility that merges results from both search methods, ensuring the most relevant documents stay at the top.

### 🧠 LLM Orchestration
-   **Groq Integration**: Using the Groq API for lightning-fast inference (Llama-3.3-70b-versatile).
-   **Streaming Response**: Implemented asynchronous streaming to provide a "typing" effect in the frontend, reducing perceived latency.

---

## 📂 Component Breakdown

### 1. Data Store Layer (`app/db/`)
-   **ChromaDB (`vector_store.py`)**: Persistently stores legal document chunks and their vector embeddings.
-   **Supabase (`session_store.py`)**: Manages conversation history, allowing the AI to remember context across multiple turns in a session.

### 2. Ingestion Pipeline (`scrapers/`)
A multi-stage pipeline to populate the system with legal data:
-   **Crawler (`crawler.py`)**: An asynchronous crawler built on **Playwright** to handle dynamic web content and browser-level interactions.
-   **HTML Parser (`html_parser.py`)**: Uses BeautifulSoup to extract structured data (Act, Section, Title, Content) from raw HTML pages.
-   **Devgan Scraper (`sources/devgan.py`)**: A specific implementation targeting IPC (Indian Penal Code) sections.
-   **Master Pipeline (`pipeline.py`)**: Orchestrates the full "Scrape -> Embed -> Save" flow.

### 3. Utility Suite (`app/utils/`)
-   **Embedder**: Singleton class for generating consistent embeddings for documents and user queries.
-   **Prompt Builder**: Manages complex system instructions and handles the aggregation of context chunks into the final LLM prompt.
-   **RRF & BM25**: Algorithms for ranking and merging search results.

---

## 🚀 API Endpoints (`app/api/`)

The FastAPI application exposes the following key endpoints:
-   `POST /api/chat`: The core endpoint. Accepts a user query and `session_id`, returns a `text/event-stream` of tokens.
-   `GET /api/history/{session_id}`: Retrieves previous messages for a specific session from Supabase.
-   `DELETE /api/session/{session_id}`: Clears the conversation history for a given session.
-   `GET /api/health`: Basic health check for deployment monitoring.

## 🛠️ Developer Scripts
-   `scripts/run_ingestion.py`: A CLI tool to manually trigger the data pipeline (e.g., `uv run python scripts/run_ingestion.py --source devgan`).

---

## 📝 Current Status & Configuration
- **Dependencies**: Managed via `uv` and `pyproject.toml`.
- **Environment**: All secrets and configurations are driven by `.env`.
- **Status**: Backend core is ready. Real-world ingestion and chat streaming are fully implemented and await valid API keys for execution.

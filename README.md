# 🏛️ Legal AI RAG Backend

A premium, FastAPI-powered **Retrieval-Augmented Generation (RAG)** engine for the Indian Law AI Chatbot. This system leverages **ChromaDB** for high-performance vector storage and **Groq's Llama models** for state-of-the-art response generation.

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.13+** (Optimized for latest Python features)
- **[uv](https://github.com/astral-sh/uv)** — The lightning-fast Python package and project manager.
- **Groq API Key** — Obtain yours at [console.groq.com](https://console.groq.com/keys).

### 2. Installation
Initialize the project environment and install dependencies in one command:
```powershell
uv sync
```
This command sets up a synchronized virtual environment (`.venv`) based on the `pyproject.toml` and `uv.lock`.

### 3. Configuration
Set up your environment variables by creating a `.env` file in the root:
```env
GROQ_API_KEY=your_groq_api_key_here
CHROMA_DB_PATH=./chroma_db
```
> [!TIP]
> Ensure `CHROMA_DB_PATH` points to a directory where you want the vector data persisted.

### 4. Running the Server
Launch the development server with hot-reload enabled:
```powershell
uv run uvicorn main:app --reload
```
The API will be live at `http://127.0.0.1:8000`. You can explore the interactive API documentation at `http://127.0.0.1:8000/docs`.

---

## 📁 Project Overview

```text
backend/
├── app/
│   ├── api/          # Route handlers (Chat, Health)
│   ├── core/         # Configuration logic (Pydantic Settings)
│   ├── db/           # Vector store connector (ChromaDB)
│   ├── docs/         # Detailed project documentation
│   └── services/      # RAG orchestrator & Groq LLM client
├── main.py           # Application entry point
├── pyproject.toml    # Modern package management
├── uv.lock           # Locked dependency versions
└── .env              # Local environment variables (gitignored)
```

---

## 📖 Deep Dive Documentation
- [Project Setup Guide](app/docs/PROJECT_SET_UP.md) — Detailed environment setup.
- [Folder Structure Blueprint](app/docs/folder-structure.md) — Comprehensive future architectural plan.
- [Architecture Specs](app/docs/legal-ai-architecture.md) — Technical RAG design details.

---
*Built with ❤️ for the Legal AI Ecosystem.*

## ⚡ Quick Start Execution

If you want to get started immediately, run these commands in order:

```powershell
uv venv
source .venv/Scripts/activate
uv add -r requirements.txt
uv run uvicorn main:app --reload
```

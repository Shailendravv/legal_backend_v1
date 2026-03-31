# Indian Legal AI Chatbot — Complete Architecture (HDL + LDL)

> **Document Purpose:** This file is written for both humans and AI agents.
> Every section is structured so a developer can implement it directly, and an AI coding assistant can use it as a precise specification with zero ambiguity.
>
> **Product:** AI-powered legal chatbot for Indian law (starting with IPC — Indian Penal Code).
> **Stack:** React (frontend) · FastAPI + Python (backend + AI) · Groq LLM · ChromaDB · LangGraph
> **Constraint:** 100% free and open-source.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [High-Level Design (HDL)](#2-high-level-design-hdl)
3. [Tech Stack Decisions](#3-tech-stack-decisions)
4. [Data Sources](#4-data-sources)
5. [Data Ingestion Pipeline (LDL)](#5-data-ingestion-pipeline-ldl)
6. [RAG Engine (LDL)](#6-rag-engine-ldl)
7. [LangGraph Agent (LDL)](#7-langgraph-agent-ldl)
8. [Vector Database (LDL)](#8-vector-database-ldl)
9. [FastAPI Backend (LDL)](#9-fastapi-backend-ldl)
10. [React Frontend (LDL)](#10-react-frontend-ldl)
11. [Deployment Strategy](#11-deployment-strategy)
12. [Security and Compliance](#12-security-and-compliance)
13. [Future Improvements](#13-future-improvements)

---

## 1. System Overview

### What this system does

A user types a legal question in English (e.g. "What is Section 302 IPC?" or "My neighbor stole my bike and threatened me — what can I do?"). The system retrieves accurate, grounded answers from real Indian legal documents and streams the response back in real time. Every answer cites the exact IPC section it came from.

### Core design philosophy

- **Hybrid RAG first, Agents when needed.** Simple queries use a fast RAG pipeline. Complex multi-act or scenario-based queries escalate to a LangGraph agent.
- **Grounding over generation.** The LLM is instructed to answer ONLY from retrieved legal text. If information is not in the retrieved context, the system says so.
- **Section-level chunking.** Legal documents are never split by character count. Each IPC/BNS section is its own retrieval unit.
- **Zero paid APIs.** Groq free tier, ChromaDB open source, HuggingFace free models, Render/Vercel free hosting.

---

## 2. High-Level Design (HDL)

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER (Browser)                           │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTPS / SSE stream
┌──────────────────────────────▼──────────────────────────────────┐
│              FRONTEND — React  (Vercel, free CDN)               │
│  Chat UI · Streaming render · Session UUID · Shadcn/Tailwind    │
└──────────────────────────────┬──────────────────────────────────┘
                               │ REST POST /chat
┌──────────────────────────────▼──────────────────────────────────┐
│           BACKEND API GATEWAY — FastAPI  (Render, free)         │
│   POST /chat · GET /history · StreamingResponse · CORS guard    │
└──────────┬───────────────────────────────────────┬──────────────┘
           │ simple query                           │ complex/scenario
┌──────────▼──────────────┐           ┌────────────▼──────────────┐
│      RAG ENGINE         │           │    LANGGRAPH AGENT        │
│  Hybrid retrieval       │           │  Query router             │
│  Context builder        │           │  Multi-act retrieval      │
│  Prompt templating      │           │  Fact-checker node        │
└──────────┬──────────────┘           └────────────┬──────────────┘
           │                                       │
           └──────────────┬────────────────────────┘
                          │
        ┌─────────────────▼──────────────────────────┐
        │            ChromaDB (in-process)            │
        │  Vector store · Metadata filter · BM25      │
        └─────────────────┬──────────────────────────┘
                          │ top-k chunks + metadata
        ┌─────────────────▼──────────────────────────┐
        │         GROQ LLM — Llama 3 70B             │
        │  Streamed inference · Citation enforcement  │
        └─────────────────┬──────────────────────────┘
                          │ SSE token stream
                    back to FastAPI → React UI

═══════════════════ OFFLINE DATA PIPELINE ═══════════════════════

  Legal Sources → Playwright Crawler → PDF/HTML Parser
  → Cleaner → Section Chunker → Metadata Tagger
  → BAAI/bge-small-en-v1.5 Embedder → ChromaDB Upsert

  Sources: India Code · Devgan.in · MHA.gov.in
           HuggingFace 169Pi/indian_law · Kaggle

═════════════════════ SESSION MEMORY ════════════════════════════

  Supabase (PostgreSQL free tier)
  Stores: session_id, conversation history (JSONB), TTL 30 days
```

---

## 3. Tech Stack Decisions

| Component | Choice | Why |
|---|---|---|
| **LLM** | Llama 3 70B via Groq | Fastest inference, strong legal reasoning, free tier |
| **Embedding model** | BAAI/bge-small-en-v1.5 | #1 MTEB Retrieval leaderboard for its size, runs on CPU |
| **Vector DB** | ChromaDB (MVP) → Qdrant (scale) | Zero setup, native LangChain integration, metadata filtering |
| **Agent framework** | LangGraph | Stateful multi-step graphs, native LangChain interop |
| **Backend** | FastAPI (Python 3.11) | Async, StreamingResponse, Pydantic validation |
| **Frontend** | React + Vite | Fast, component-based, easy SSE integration |
| **UI library** | Shadcn/UI + Tailwind CSS | Professional legal-tech aesthetic, free |
| **Session store** | Supabase (free PostgreSQL) | Managed, free 500MB, JSONB for conversation history |
| **Frontend deploy** | Vercel | Global CDN, zero-config, free |
| **Backend deploy** | Render | Free Web Service, Docker support |
| **Scraping** | Playwright (Python) | Handles JS-rendered government sites |
| **PDF parsing** | Marker / PyMuPDF4LLM | High-accuracy Markdown from legal PDFs |

---

## 4. Data Sources

### 4.1 Primary sources

| Source | URL | Data Type | Format | Scraping Status |
|---|---|---|---|---|
| India Code | indiacode.nic.in | All Central/State Acts (IPC, BNS, CrPC) | HTML + PDF | Allowed (public) |
| Devgan.in | devgan.in | IPC section-by-section breakdown with explanations | HTML | Good for scraping |
| MHA.gov.in | mha.gov.in | Ministry of Home Affairs circulars and acts | PDF | Allowed |
| IndianKanoon | indiankanoon.org | Court judgments and case law | HTML | Check robots.txt |
| HuggingFace | 169Pi/indian_law | 50M tokens of Indian jurisprudence with reasoning traces | Parquet/JSON | Direct download |
| Kaggle | akshatgupta7/llm-fine-tuning-dataset-of-indian-legal-texts | Curated IPC/CrPC QA pairs | CSV | Direct download |

### 4.2 DPDPA 2023 compliance note

> Scraping **publicly available** legal text for an AI research/legal-assistance tool is permitted under India's Digital Personal Data Protection Act (DPDPA) 2023. However:
> - **Never scrape PII** (names, addresses, UID numbers) from court case documents.
> - Use only the statutory legal text (acts, sections, judgments as official records).
> - Anonymize any incidentally captured personal data before storage.

---

## 5. Data Ingestion Pipeline (LDL)

### 5.1 Pipeline flow

```
Legal Source (URL / PDF file)
    │
    ▼
[Step 1] Playwright Crawler
    - Async crawl HTML pages (handles JS-rendered govt sites)
    - Download PDF links
    - Respect robots.txt delay settings
    │
    ▼
[Step 2] Content Extractor
    - HTML pages   → BeautifulSoup4 → raw text
    - PDF files    → Marker (preferred) or PyMuPDF4LLM → Markdown
    - CSV/Parquet  → pandas → DataFrame rows
    │
    ▼
[Step 3] Cleaner
    - Remove PDF headers/footers (page numbers, court stamps)
    - Strip HTML navigation elements
    - Normalize whitespace and unicode
    - Remove or flag PII patterns (regex: Aadhaar, phone, email)
    │
    ▼
[Step 4] Section Chunker
    - Strategy: ONE IPC/BNS section = ONE chunk
    - Tool: MarkdownHeaderTextSplitter (split on ## Section headings)
    - For long sections (e.g. Section 300): split by subsection (###)
    - NEVER chunk by character count alone — legal logic breaks across arbitrary splits
    │
    ▼
[Step 5] Metadata Tagger
    - Attach structured metadata to each chunk
    │
    ▼
[Step 6] Embedder
    - Model: BAAI/bge-small-en-v1.5 (sentence-transformers)
    - Instruction prefix: "Represent this legal passage for retrieval: "
    - Output: 384-dimensional float32 vector
    │
    ▼
[Step 7] ChromaDB Upsert
    - Collection: "indian_legal_docs"
    - Upsert by chunk_id (idempotent — safe to re-run)
```

### 5.2 Chunk JSON schema

Every chunk stored in ChromaDB must conform to this exact schema:

```json
{
  "chunk_id":   "IPC-420-01",
  "act":        "IPC",
  "section":    "420",
  "title":      "Cheating and dishonestly inducing delivery of property",
  "content":    "Whoever cheats and thereby dishonestly induces the person deceived...",
  "punishment": "Imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine",
  "type":       "Cognizable",
  "bailable":   false,
  "category":   "Fraud",
  "source_url": "https://indiacode.nic.in/handle/123456789/2351",
  "year":       1860
}
```

> **For AI agents:** When upserting to ChromaDB, the `document` field = `content`, and all other fields go into `metadatas`. The `chunk_id` is the ChromaDB `id`. This schema is the contract between the ingestion pipeline and the retrieval engine — do not add or remove fields without updating the retrieval filter logic.

### 5.3 Scraping tools

```python
# requirements for scrapers
playwright==1.44.0          # JS-capable crawler
beautifulsoup4==4.12.3      # HTML parser
marker-pdf==0.2.17          # PDF → Markdown (preferred)
PyMuPDF==1.24.5             # PDF fallback
unstructured[pdf]==0.14.0   # Section partitioning
pandas==2.2.2               # CSV/Parquet processing
datasets==2.19.0            # HuggingFace datasets
```

---

## 6. RAG Engine (LDL)

### 6.1 Retrieval flow

```
User query string
    │
    ▼
[Step 1] Query Embedder
    - Embed query with BAAI/bge-small-en-v1.5
    - Prefix: "Represent this legal question for searching: "
    │
    ▼
[Step 2] Metadata Filter Decision
    - Does query mention a specific act? ("IPC", "BNS", "CrPC")
    - If yes → add ChromaDB where={"act": {"$eq": "IPC"}} filter
    - If query contains "Section NNN" → add where={"section": {"$eq": "NNN"}}
    │
    ▼
[Step 3] Parallel Search
    ├── Vector search: ChromaDB cosine similarity, n_results=10
    └── BM25 keyword search: rank-bm25 over all stored document texts
    │
    ▼
[Step 4] RRF Re-ranking (Reciprocal Rank Fusion)
    - Merge vector rank list + BM25 rank list
    - score = 1/(k + rank_vector) + 1/(k + rank_bm25)  [k=60]
    - Select top 5 chunks by merged score
    │
    ▼
[Step 5] Context Builder
    - Format: "Section {section}, {act} ({year}): {content}"
    - Concatenate top-5 chunks with separator lines
    - Trim to stay within 4096 token context window
    │
    ▼
[Step 6] Prompt Builder
    - Inject system prompt template (see below)
    - Inject retrieved context
    - Inject conversation history (last 5 turns)
    - Inject current user query
    │
    ▼
[Step 7] Groq LLM Inference (stream=True)
    │
    ▼
[Step 8] Self-Correction Check
    - Before streaming: does the draft answer contradict retrieved text?
    - If contradiction detected: re-invoke LLM with stricter prompt
    │
    ▼
Stream tokens to FastAPI → SSE to React UI
```

### 6.2 System prompt template

```
SYSTEM PROMPT:
You are a Senior Legal Assistant specializing in Indian criminal and civil law.
Your knowledge comes exclusively from Indian legal statutes and acts.

STRICT RULES — follow these without exception:
1. Answer ONLY using the legal sections provided in CONTEXT below.
2. Every factual claim MUST be followed by its citation: [Section X, IPC] or [Section X, BNS].
3. If the answer cannot be found in the provided context, respond exactly:
   "I don't have sufficient information in my knowledge base to answer this accurately.
    Please consult a qualified advocate."
4. Never fabricate section numbers, punishments, or legal interpretations.
5. Use plain English. Avoid unnecessary legal jargon unless quoting a statute directly.
6. Always end your response with:
   "⚠ Disclaimer: This information is for educational purposes only and does not
    constitute legal advice. Consult a qualified legal professional for your specific situation."

CONTEXT (retrieved legal sections):
{retrieved_context}

CONVERSATION HISTORY:
{history}

USER QUESTION:
{user_query}
```

### 6.3 Embedding model usage

```python
from sentence_transformers import SentenceTransformer

# Load once at application startup
model = SentenceTransformer("BAAI/bge-small-en-v1.5")

# For indexing (documents)
def embed_document(text: str) -> list[float]:
    instruction = "Represent this legal passage for retrieval: "
    return model.encode(instruction + text, normalize_embeddings=True).tolist()

# For querying (user questions)
def embed_query(text: str) -> list[float]:
    instruction = "Represent this legal question for searching: "
    return model.encode(instruction + text, normalize_embeddings=True).tolist()
```

---

## 7. LangGraph Agent (LDL)

### 7.1 When to use simple RAG vs LangGraph

| Query type | Example | Route |
|---|---|---|
| Direct factual | "What is Section 302 IPC?" | Simple RAG |
| Definition | "Explain IPC Section 375 simply" | Simple RAG |
| Punishment lookup | "What is the punishment for theft?" | Simple RAG |
| Scenario-based | "My neighbor stole my bike and threatened me — what sections apply?" | LangGraph Agent |
| Cross-act reasoning | "How do General Exceptions (Chapter IV) affect Section 378?" | LangGraph Agent |
| Comparison | "Difference between IPC Section 302 and BNS Section 101?" | LangGraph Agent |

> **Decision rule for AI agents:** If the query contains scenario keywords ("what can I do", "my neighbor", "if someone", "how does X affect Y") OR references more than one legal act, route to LangGraph. Otherwise use simple RAG.

### 7.2 LangGraph node design

```
[Node 1: Query Analyser]
  Input:  user query string
  Task:   - Classify intent: "factual" | "scenario" | "comparison"
          - Extract entities: section numbers, act names, offense type
          - Determine if multi-act reasoning is needed
  Output: {intent, acts_needed: ["IPC", "BNS"], entities: ["420", "theft"]}

          ↓

[Node 2: Act Router]
  Input:  acts_needed list
  Task:   - Map each act to ChromaDB metadata filter
          - Decide parallel vs sequential retrieval
  Output: {retrieval_plan: [{act: "IPC", filter: {...}}, ...]}

          ↓

[Node 3: Parallel Retriever]
  Input:  retrieval_plan
  Task:   - Execute hybrid RAG retrieval for each act simultaneously
          - Use asyncio.gather for parallel execution
  Output: {docs_by_act: {"IPC": [...chunks], "BNS": [...chunks]}}

          ↓

[Node 4: Fact-Checker]
  Input:  all retrieved chunks
  Task:   - Check: do any retrieved sections contradict each other?
          - Flag conflicts for the synthesiser
          - If critical contradiction: add warning to response
  Output: {verified_docs, conflicts: [...]}

          ↓

[Node 5: Response Synthesiser]
  Input:  verified_docs, conflicts, original query
  Task:   - Build merged context from all retrieved chunks
          - Call Groq LLM with multi-act prompt
          - Stream response with citations
  Output: streamed token generator
```

### 7.3 LangGraph state schema

```python
from typing import TypedDict, Optional

class LegalAgentState(TypedDict):
    # Input
    query:          str
    session_id:     str
    history:        list[dict]          # [{"role": "user"|"assistant", "content": "..."}]

    # Analysis
    intent:         str                 # "factual" | "scenario" | "comparison"
    acts_needed:    list[str]           # ["IPC", "BNS", "General_Exceptions"]
    entities:       dict                # {"sections": ["302", "420"], "offenses": ["murder"]}

    # Retrieval
    retrieval_plan: list[dict]
    docs_by_act:    dict[str, list]     # {"IPC": [chunk1, chunk2, ...]}

    # Verification
    verified_docs:  list[dict]
    conflicts:      list[str]           # human-readable conflict descriptions

    # Output
    final_answer:   Optional[str]
    citations:      list[str]           # ["Section 302, IPC", "Section 101, BNS"]
    error:          Optional[str]
```

---

## 8. Vector Database (LDL)

### 8.1 Comparison

| Database | Type | Pros | Cons | Recommendation |
|---|---|---|---|---|
| **ChromaDB** | In-process | Zero setup, native LangChain, metadata filtering, runs inside FastAPI | Single-node, harder to scale past ~500K vectors | **Use for MVP** |
| **FAISS** | In-memory | Extremely fast, Meta-backed | No metadata filtering, no native persistence | Avoid — cannot filter by act/section |
| **Qdrant** | Server (Rust) | Best filtering, high performance, production-grade | Needs Docker or cloud setup | Use when scaling past MVP |
| **Weaviate** | Server | GraphQL API, multi-modal | Heavy resource usage | Overkill for MVP |

### 8.2 ChromaDB collection configuration

```python
import chromadb
from chromadb.config import Settings

# Initialize (persists to disk)
client = chromadb.PersistentClient(path="/data/chroma")

# Create or get collection
collection = client.get_or_create_collection(
    name="indian_legal_docs",
    metadata={"hnsw:space": "cosine"}   # cosine similarity for embeddings
)

# Upsert a chunk
collection.upsert(
    ids=["IPC-420-01"],
    embeddings=[embed_document(chunk["content"])],
    documents=[chunk["content"]],
    metadatas=[{
        "act":        chunk["act"],
        "section":    chunk["section"],
        "title":      chunk["title"],
        "category":   chunk["category"],
        "type":       chunk["type"],
        "bailable":   str(chunk["bailable"]),
        "source_url": chunk["source_url"],
    }]
)

# Query with metadata filter
results = collection.query(
    query_embeddings=[embed_query(user_query)],
    where={"act": {"$eq": "IPC"}},      # metadata filter
    n_results=10,
    include=["documents", "metadatas", "distances"]
)
```

### 8.3 Migration path

```
MVP Phase      → ChromaDB PersistentClient, stored on Render disk
Scale Phase    → Qdrant Cloud free tier (1GB, no server management)
Production     → Self-hosted Qdrant on a VPS (DigitalOcean $6/mo)
```

> **For AI agents:** Migration from ChromaDB to Qdrant requires only changing the vector store adapter in `db/vector_store.py`. LangChain's `Chroma` and `Qdrant` wrappers share the same `.similarity_search()` interface. No other code changes needed.

---

## 9. FastAPI Backend (LDL)

### 9.1 API routes

| Method | Route | Auth | Description |
|---|---|---|---|
| `POST` | `/chat` | None (rate limited) | Main chat endpoint — returns SSE stream |
| `GET` | `/history/{session_id}` | None | Get last N conversation turns |
| `DELETE` | `/session/{session_id}` | None | Clear user session |
| `POST` | `/ingest` | API key | Trigger offline ingestion pipeline |
| `GET` | `/health` | None | Health check for Render zero-downtime deploy |

### 9.2 POST /chat — request and response

```python
# Request schema
class ChatRequest(BaseModel):
    query:      str        = Field(..., min_length=3, max_length=1000)
    session_id: str        = Field(..., description="UUID from client localStorage")

# Response: StreamingResponse (text/event-stream)
# Each chunk: "data: {token}\n\n"
# Final chunk: "data: [DONE]\n\n"
```

### 9.3 Chat endpoint processing flow

```python
@router.post("/chat")
async def chat(request: ChatRequest):
    # 1. Load session history from Supabase
    history = await session_store.get_history(request.session_id, last_n=5)

    # 2. Classify query complexity
    intent = query_classifier.classify(request.query)

    # 3. Route to RAG or Agent
    if intent in ("factual", "definition"):
        token_generator = rag_engine.query(request.query, history)
    else:
        token_generator = agent_runner.run(request.query, history, request.session_id)

    # 4. Stream response while saving to Supabase
    async def stream_and_save():
        full_response = ""
        async for token in token_generator:
            full_response += token
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"
        await session_store.save_turn(request.session_id, request.query, full_response)

    return StreamingResponse(stream_and_save(), media_type="text/event-stream")
```

### 9.4 Key dependencies (requirements.txt)

```
fastapi==0.111.0
uvicorn[standard]==0.30.1
pydantic==2.7.1
python-dotenv==1.0.1

# AI / RAG
langchain==0.2.5
langgraph==0.1.14
langchain-groq==0.1.6
langchain-community==0.2.5
chromadb==0.5.0
sentence-transformers==3.0.1
rank-bm25==0.2.2

# Data scraping
playwright==1.44.0
beautifulsoup4==4.12.3
marker-pdf==0.2.17
PyMuPDF==1.24.5
datasets==2.19.0
pandas==2.2.2

# Database
supabase==2.4.6

# Rate limiting
slowapi==0.1.9
```

---

## 10. React Frontend (LDL)

### 10.1 Key components

| Component | File | Responsibility |
|---|---|---|
| `ChatWindow` | `components/ChatWindow.jsx` | Scrollable message list, auto-scroll, renders message bubbles |
| `MessageBubble` | `components/MessageBubble.jsx` | User vs AI styling, renders Markdown, shows citation chips |
| `InputBar` | `components/InputBar.jsx` | Textarea, send button, loading state, Enter key handler |
| `CitationCard` | `components/CitationCard.jsx` | Expandable panel showing raw retrieved legal text |
| `LegalDisclaimer` | `components/LegalDisclaimer.jsx` | Persistent disclaimer banner (mandatory) |
| `useChat` | `hooks/useChat.js` | Core hook: sends request, reads SSE stream, updates messages |
| `useSession` | `hooks/useSession.js` | UUID generation + localStorage persistence |
| `chatApi` | `api/chatApi.js` | fetch() wrapper with ReadableStream SSE reader |

### 10.2 SSE streaming implementation

```javascript
// api/chatApi.js
export async function streamChat(query, sessionId, onToken, onDone, onError) {
  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, session_id: sessionId }),
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split("\n\n").filter(Boolean);

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const token = line.replace("data: ", "");
          if (token === "[DONE]") { onDone(); return; }
          onToken(token);
        }
      }
    }
  } catch (err) {
    onError(err.message);
  }
}
```

### 10.3 Session handling

```javascript
// hooks/useSession.js
import { v4 as uuidv4 } from "uuid";

export function useSession() {
  const SESSION_KEY = "legal_ai_session_id";

  const getSessionId = () => {
    let id = localStorage.getItem(SESSION_KEY);
    if (!id) {
      id = uuidv4();
      localStorage.setItem(SESSION_KEY, id);
    }
    return id;
  };

  const clearSession = () => {
    const newId = uuidv4();
    localStorage.setItem(SESSION_KEY, newId);
    return newId;
  };

  return { sessionId: getSessionId(), clearSession };
}
```

### 10.4 Key npm dependencies

```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-markdown": "^9.0.1",
    "uuid": "^10.0.0",
    "zustand": "^4.5.4",
    "lucide-react": "^0.383.0",
    "tailwindcss": "^3.4.4",
    "@radix-ui/react-slot": "^1.1.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.1",
    "vite": "^5.3.1"
  }
}
```

---

## 11. Deployment Strategy

### 11.1 Free-tier architecture

| Layer | Platform | Free Tier Limits | Notes |
|---|---|---|---|
| **Frontend** | Vercel | Unlimited deployments, global CDN | Connect GitHub repo, auto-deploy on push |
| **Backend** | Render | 512MB RAM, sleeps after 15 min idle | Use UptimeRobot (free) to ping every 14 min |
| **Session DB** | Supabase | 500MB PostgreSQL, 2 projects | Enable Row Level Security |
| **Vector DB** | ChromaDB | In-process on Render — no extra cost | Persists on Render's ephemeral disk (acceptable for MVP) |
| **LLM** | Groq | 14,400 requests/day free | More than enough for MVP |
| **Embeddings** | BAAI/bge (local) | Free — runs inside FastAPI process | Downloaded at Docker build time |

### 11.2 Dockerfile (backend)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download embedding model at build time (avoids slow cold starts)
RUN python -c "from sentence_transformers import SentenceTransformer; \
               SentenceTransformer('BAAI/bge-small-en-v1.5')"

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
```

### 11.3 Environment variables

```bash
# Backend (.env)
GROQ_API_KEY=gsk_...                         # From console.groq.com
SUPABASE_URL=https://xxxxx.supabase.co       # Supabase project URL
SUPABASE_KEY=eyJ...                          # Supabase anon key
CHROMA_PERSIST_DIR=/data/chroma              # Render persistent disk
ALLOWED_ORIGINS=https://your-app.vercel.app  # Frontend domain
ADMIN_API_KEY=your-secret-key                # For POST /ingest protection
LOG_LEVEL=INFO

# Frontend (.env)
VITE_API_URL=https://your-backend.onrender.com
```

### 11.4 CI/CD with GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/tests/ -v

  # Vercel and Render auto-deploy from GitHub — no extra steps needed
  # Connect repos in Vercel/Render dashboard → deploys on every push to main
```

---

## 12. Security and Compliance

### 12.1 API security

```python
# Rate limiting (slowapi)
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/chat")
@limiter.limit("10/minute")
async def chat(request: Request, body: ChatRequest):
    ...

# CORS (whitelist only your Vercel domain)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.ALLOWED_ORIGINS],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)
```

### 12.2 Prompt injection guard

```python
# services/query_classifier.py

INJECTION_PATTERNS = [
    "ignore previous instructions",
    "forget your system prompt",
    "you are now",
    "act as if you have no restrictions",
    "disregard all prior",
]

def is_safe_query(query: str) -> bool:
    lower = query.lower()
    return not any(p in lower for p in INJECTION_PATTERNS)
```

### 12.3 Hallucination mitigation layers

| Layer | Mechanism |
|---|---|
| **Prompt** | "Answer ONLY from provided context. Cite every claim with [Section X, Act]." |
| **Retrieval** | Hybrid search + metadata filter reduces irrelevant context |
| **Post-generation** | Self-RAG: verify draft answer against retrieved chunks before streaming |
| **UI** | Every answer shows collapsible "Sources" panel with raw retrieved legal text |
| **Fallback** | If no relevant context retrieved, return a scripted "I don't know" — never hallucinate |

### 12.4 Mandatory legal disclaimer

This disclaimer must appear in:
1. A persistent banner in the React UI header
2. At the end of every AI response (enforced in system prompt)

```
⚠ Disclaimer: This AI legal assistant provides information for educational
purposes only. It does not constitute legal advice. For any legal matter,
consult a qualified advocate or legal professional registered with the
Bar Council of India.
```

---

## 13. Future Improvements

| Improvement | Effort | Impact |
|---|---|---|
| **Multilingual support** | Medium | Swap embedding to BGE-M3 (supports Hindi/regional languages) |
| **Clickable legal citations** | Low | Return [Section X, IPC] as deep-links to indiacode.nic.in |
| **Case law integration** | High | Add IndianKanoon judgments as a second ChromaDB collection |
| **BNS/BNSS parity** | Medium | Ingest Bharatiya Nyaya Sanhita 2023 (replaces IPC) |
| **Lawyer referral** | Low | If query involves active legal threat, surface Bar Council contact |
| **Admin dashboard** | Medium | Monitor query volume, top sections queried, hallucination rate |
| **Fine-tuned model** | High | Fine-tune Llama 3 on the Kaggle IPC QA dataset for domain accuracy |

---

*Document version: 1.0 — Designed for MVP implementation.*
*Both humans and AI coding assistants should use this as the single source of truth for all architecture decisions.*

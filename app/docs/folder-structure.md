# Indian Legal AI Chatbot — Folder & File Structure

> **Purpose:** This document defines the exact folder and file structure for all three deployment units.
> Every file listed here has a description of what it does and what code it should contain.
> Use this as the implementation blueprint — create files in this exact structure.
>
> **Deployment model:**
> - `frontend/` → Deployed on **Vercel** (React + Vite)
> - `backend/` → Deployed on **Render** (FastAPI + ChromaDB + LangGraph)
>
> **Repository structure:** Two separate GitHub repos (one per deploy unit) OR a monorepo with two root-level folders.

---

## Repository Layout (Monorepo)

```
legal-ai-chatbot/                          ← Root repo (GitHub)
├── frontend/                              ← React app → Vercel
├── backend/                               ← FastAPI app → Render
├── .github/
│   └── workflows/
│       └── deploy.yml                     ← CI/CD pipeline
└── README.md                              ← Project overview
```

---

## UNIT 1: `frontend/` — React App (Vercel)

```
frontend/
├── public/
│   ├── favicon.ico
│   └── logo.svg                           ← Legal AI brand logo (scales of justice SVG)
│
├── src/
│   │
│   ├── api/
│   │   └── chatApi.js                     ← All HTTP calls to FastAPI backend
│   │                                         - streamChat(query, sessionId, onToken, onDone, onError)
│   │                                         - getHistory(sessionId)
│   │                                         - clearSession(sessionId)
│   │
│   ├── components/
│   │   ├── ChatWindow.jsx                 ← Scrollable message list
│   │   │                                     - Renders list of MessageBubble components
│   │   │                                     - Auto-scrolls to bottom on new message/token
│   │   │                                     - Shows loading skeleton while streaming
│   │   │
│   │   ├── MessageBubble.jsx              ← Single message (user or AI)
│   │   │                                     - user: right-aligned blue bubble
│   │   │                                     - ai: left-aligned white card with Markdown render
│   │   │                                     - Shows citation chips: [Section 302, IPC]
│   │   │                                     - Renders <CitationCard> when chip is clicked
│   │   │
│   │   ├── InputBar.jsx                   ← Text input + send button
│   │   │                                     - Textarea with auto-resize
│   │   │                                     - Ctrl+Enter to send
│   │   │                                     - Disabled + spinner while streaming
│   │   │                                     - Character count (max 1000)
│   │   │
│   │   ├── CitationCard.jsx               ← Expandable source panel
│   │   │                                     - Shows raw retrieved legal text
│   │   │                                     - Displays: act, section, title, source_url
│   │   │                                     - "View on India Code" external link
│   │   │
│   │   ├── LegalDisclaimer.jsx            ← Persistent top banner (MANDATORY)
│   │   │                                     - ⚠ "For informational purposes only..."
│   │   │                                     - Cannot be dismissed (legal requirement)
│   │   │
│   │   ├── Header.jsx                     ← App header
│   │   │                                     - Logo + app name "LegalAI India"
│   │   │                                     - "New Chat" button (calls clearSession)
│   │   │
│   │   └── ErrorBanner.jsx                ← Error display
│   │                                         - Shows API errors inline in chat
│   │                                         - Network error / rate limit message
│   │
│   ├── hooks/
│   │   ├── useChat.js                     ← Core chat logic hook
│   │   │                                     - State: messages[], isStreaming, error
│   │   │                                     - sendMessage(query): calls chatApi.streamChat
│   │   │                                     - Appends AI message token-by-token to state
│   │   │                                     - Handles [DONE] signal
│   │   │
│   │   └── useSession.js                  ← Session UUID management
│   │                                         - getSessionId(): reads from localStorage or creates uuid v4
│   │                                         - clearSession(): generates new UUID, saves to localStorage
│   │                                         - Key: "legal_ai_session_id"
│   │
│   ├── store/
│   │   └── chatStore.js                   ← Zustand global state store
│   │                                         - messages: Message[]
│   │                                         - isStreaming: boolean
│   │                                         - error: string | null
│   │                                         - addUserMessage(text)
│   │                                         - appendAIToken(token)
│   │                                         - setError(msg)
│   │                                         - clearMessages()
│   │
│   ├── utils/
│   │   ├── parseStream.js                 ← SSE chunk parser
│   │   │                                     - parseSseLine(line): extracts token from "data: {token}"
│   │   │                                     - Handles [DONE] sentinel
│   │   │
│   │   └── formatCitations.js             ← Citation string parser
│   │                                         - extractCitations(text): finds [Section X, IPC] patterns
│   │                                         - Returns array of {section, act, display} objects
│   │
│   ├── constants/
│   │   └── config.js                      ← App configuration constants
│   │                                         - API_URL: import.meta.env.VITE_API_URL
│   │                                         - MAX_QUERY_LENGTH: 1000
│   │                                         - MAX_HISTORY_TURNS: 10
│   │
│   ├── App.jsx                            ← Root component
│   │                                         - Layout: <Header> + <LegalDisclaimer> + <ChatWindow> + <InputBar>
│   │                                         - Passes useChat and useSession to children
│   │
│   └── main.jsx                           ← Vite entry point
│                                             - ReactDOM.createRoot, renders <App />
│
├── .env                                   ← Local dev environment (gitignored)
│                                             VITE_API_URL=http://localhost:8000
│
├── .env.production                        ← Production overrides (Vercel reads this)
│                                             VITE_API_URL=https://your-backend.onrender.com
│
├── vercel.json                            ← Vercel config
│                                             - rewrites: /api/* → backend URL (avoids CORS in prod)
│                                             - framework: "vite"
│
├── tailwind.config.js                     ← Tailwind CSS config
│                                             - extend colors: brand gold + legal dark blue
│
├── index.html                             ← Vite HTML entry (meta tags, title "LegalAI India")
├── vite.config.js                         ← Vite config (React plugin, proxy for local dev)
├── package.json                           ← npm dependencies
└── .gitignore
```

### `vercel.json` content

```json
{
  "rewrites": [
    { "source": "/api/:path*", "destination": "https://your-backend.onrender.com/:path*" }
  ],
  "framework": "vite"
}
```

### `vite.config.js` content (local dev proxy)

```javascript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
```

---

## UNIT 2: `backend/` — FastAPI App (Render)

```
backend/
│
├── app/                                   ← Main application package
│   │
│   ├── main.py                            ← FastAPI app entry point
│   │                                         - Creates FastAPI() instance
│   │                                         - Registers CORS middleware
│   │                                         - Registers rate limit middleware (slowapi)
│   │                                         - Registers routers (api/routes.py)
│   │                                         - Lifespan: loads embedding model + ChromaDB on startup
│   │                                         - GET /health endpoint
│   │
│   ├── api/
│   │   └── routes.py                      ← All API route handlers
│   │                                         - POST /chat            → chat handler
│   │                                         - GET  /history/{id}    → history handler
│   │                                         - DELETE /session/{id}  → clear session
│   │                                         - POST /ingest          → trigger pipeline (admin key)
│   │
│   ├── core/
│   │   ├── config.py                      ← Environment variables (Pydantic BaseSettings)
│   │   │                                     - GROQ_API_KEY: str
│   │   │                                     - SUPABASE_URL: str
│   │   │                                     - SUPABASE_KEY: str
│   │   │                                     - CHROMA_PERSIST_DIR: str = "/data/chroma"
│   │   │                                     - ALLOWED_ORIGINS: str
│   │   │                                     - ADMIN_API_KEY: str
│   │   │                                     - LOG_LEVEL: str = "INFO"
│   │   │
│   │   └── dependencies.py                ← FastAPI dependency injection
│   │                                         - get_vector_store(): returns ChromaDB collection singleton
│   │                                         - get_embedding_model(): returns loaded SentenceTransformer
│   │                                         - get_groq_client(): returns Groq client
│   │
│   ├── models/
│   │   └── schemas.py                     ← Pydantic request/response schemas
│   │                                         - ChatRequest(query: str, session_id: str)
│   │                                         - ChatResponse(answer: str, citations: list[str])
│   │                                         - HistoryResponse(turns: list[Turn])
│   │                                         - Turn(role: str, content: str, timestamp: datetime)
│   │                                         - IngestRequest(source: str, admin_key: str)
│   │
│   ├── services/
│   │   │
│   │   ├── query_classifier.py            ← Classify user query intent
│   │   │                                     - classify(query: str) → "factual" | "scenario" | "comparison"
│   │   │                                     - Uses keyword heuristics (fast, no LLM call)
│   │   │                                     - Patterns: scenario keywords, multi-act references
│   │   │                                     - is_safe_query(query): prompt injection guard
│   │   │
│   │   ├── rag_engine.py                  ← Simple RAG pipeline (used for factual queries)
│   │   │                                     - retrieve(query, history, filters) → async generator[str]
│   │   │                                     - Steps: embed → chroma query → BM25 → RRF → prompt → groq stream
│   │   │                                     - Returns token-by-token async generator
│   │   │
│   │   ├── agent_runner.py                ← LangGraph agent execution
│   │   │                                     - run(query, history, session_id) → async generator[str]
│   │   │                                     - Builds LegalAgentState
│   │   │                                     - Compiles and runs the LangGraph graph
│   │   │                                     - Streams final response
│   │   │
│   │   └── groq_client.py                 ← Groq LLM wrapper
│   │                                         - stream_completion(messages, system_prompt) → async generator[str]
│   │                                         - Model: llama3-70b-8192
│   │                                         - temperature: 0.1 (low for factual legal answers)
│   │                                         - max_tokens: 1024
│   │
│   ├── agents/
│   │   ├── graph.py                       ← LangGraph graph definition
│   │   │                                     - Defines StateGraph(LegalAgentState)
│   │   │                                     - Adds nodes: analyse, route, retrieve, verify, synthesise
│   │   │                                     - Adds edges and conditional routing
│   │   │                                     - Compiles to runnable graph
│   │   │
│   │   ├── nodes/
│   │   │   ├── analyser.py                ← Node 1: Query analysis
│   │   │   │                                 - analyse_query(state) → updated state
│   │   │   │                                 - Extracts: intent, acts_needed, entities
│   │   │   │
│   │   │   ├── router.py                  ← Node 2: Act routing
│   │   │   │                                 - route_acts(state) → updated state with retrieval_plan
│   │   │   │
│   │   │   ├── retriever.py               ← Node 3: Parallel retrieval
│   │   │   │                                 - retrieve_parallel(state) → updated state with docs_by_act
│   │   │   │                                 - Uses asyncio.gather for concurrent ChromaDB queries
│   │   │   │
│   │   │   ├── fact_checker.py            ← Node 4: Conflict detection
│   │   │   │                                 - check_facts(state) → updated state with conflicts list
│   │   │   │
│   │   │   └── synthesiser.py             ← Node 5: Response generation
│   │   │                                     - synthesise(state) → token stream
│   │   │                                     - Merges all docs, calls groq_client.stream_completion
│   │   │
│   │   └── state.py                       ← LegalAgentState TypedDict definition
│   │                                         - All fields as documented in architecture.md Section 7.3
│   │
│   ├── db/
│   │   ├── vector_store.py                ← ChromaDB initialization and helpers
│   │   │                                     - init_chroma() → chromadb.PersistentClient
│   │   │                                     - get_collection() → Collection singleton
│   │   │                                     - upsert_chunk(chunk_dict)
│   │   │                                     - query_similar(embedding, filters, n) → list[dict]
│   │   │                                     - get_all_documents() → list[str] (for BM25 index)
│   │   │
│   │   └── session_store.py               ← Supabase session management
│   │                                         - get_history(session_id, last_n) → list[Turn]
│   │                                         - save_turn(session_id, user_msg, ai_msg)
│   │                                         - delete_session(session_id)
│   │                                         - Table schema:
│   │                                           sessions(id UUID PK, session_id TEXT, role TEXT,
│   │                                                    content TEXT, created_at TIMESTAMPTZ)
│   │
│   └── utils/
│       ├── embedder.py                    ← Embedding utility
│       │                                     - load_model() → SentenceTransformer (singleton)
│       │                                     - embed_document(text: str) → list[float]
│       │                                     - embed_query(text: str) → list[float]
│       │                                     - embed_batch(texts: list[str]) → list[list[float]]
│       │
│       ├── bm25_index.py                  ← BM25 keyword search index
│       │                                     - build_index(docs: list[str]) → BM25Okapi
│       │                                     - search(query: str, index, docs, n) → list[dict]
│       │                                     - Index is built in memory at startup from ChromaDB docs
│       │
│       ├── rrf.py                         ← Reciprocal Rank Fusion
│       │                                     - merge_results(vector_results, bm25_results, k=60) → list[dict]
│       │                                     - Returns top-n deduplicated chunks sorted by RRF score
│       │
│       └── prompt_builder.py              ← Prompt assembly
│                                             - build_system_prompt() → str (see architecture.md §6.2)
│                                             - build_context(chunks: list[dict]) → str
│                                             - build_messages(system, context, history, query) → list[dict]
│
├── scrapers/                              ← Offline data ingestion (run manually or via /ingest)
│   ├── pipeline.py                        ← Master pipeline orchestrator
│   │                                         - run_full_pipeline(): crawl → extract → clean → chunk → embed → upsert
│   │                                         - run_source(source_name): run for one source only
│   │
│   ├── crawler.py                         ← Playwright async crawler
│   │                                         - crawl_url(url) → list[str] (downloaded HTML/PDF paths)
│   │                                         - crawl_site(base_url, depth) → list[str]
│   │                                         - respects robots.txt, adds delay between requests
│   │
│   ├── pdf_extractor.py                   ← PDF → Markdown converter
│   │                                         - extract_pdf(path) → str (Markdown)
│   │                                         - Uses Marker as primary, PyMuPDF as fallback
│   │
│   ├── html_parser.py                     ← HTML → structured text
│   │                                         - parse_devgan(html) → list[SectionDict]
│   │                                         - parse_indiacode(html) → list[SectionDict]
│   │                                         - Each parser targets the specific site's HTML structure
│   │
│   ├── cleaner.py                         ← Text cleaning
│   │                                         - clean(text) → str
│   │                                         - remove_headers_footers(text) → str
│   │                                         - remove_pii(text) → str (regex: Aadhaar, phone, email)
│   │                                         - normalize_unicode(text) → str
│   │
│   ├── chunker.py                         ← Legal section chunking
│   │                                         - chunk_by_section(markdown_text) → list[dict]
│   │                                         - Uses MarkdownHeaderTextSplitter on ## and ### headings
│   │                                         - Enforces: one IPC/BNS section = one chunk
│   │
│   ├── metadata_tagger.py                 ← JSON schema builder
│   │                                         - tag_chunk(raw_chunk, source_meta) → ChunkDict
│   │                                         - Assigns: act, section, title, category, type, bailable
│   │                                         - Generates chunk_id: "{ACT}-{SECTION}-{INDEX}"
│   │
│   └── sources/
│       ├── indiacode.py                   ← India Code specific crawler config
│       │                                     - BASE_URL, SECTION_SELECTOR, PDF_LINK_PATTERN
│       ├── devgan.py                      ← Devgan.in specific parser config
│       ├── mha.py                         ← MHA.gov.in PDF downloader
│       └── huggingface.py                 ← HuggingFace dataset downloader
│                                             - Downloads 169Pi/indian_law via datasets library
│
├── tests/
│   ├── test_routes.py                     ← FastAPI route tests (TestClient)
│   │                                         - test_health_check()
│   │                                         - test_chat_simple_query()
│   │                                         - test_chat_rate_limit()
│   │                                         - test_history_retrieval()
│   │
│   ├── test_rag_engine.py                 ← RAG pipeline unit tests
│   │                                         - test_embed_query()
│   │                                         - test_hybrid_retrieval()
│   │                                         - test_rrf_merge()
│   │                                         - test_prompt_builder()
│   │
│   ├── test_agent.py                      ← LangGraph agent tests
│   │                                         - test_query_classifier()
│   │                                         - test_full_agent_run()
│   │
│   └── conftest.py                        ← Pytest fixtures
│                                             - mock ChromaDB collection
│                                             - mock Groq client
│                                             - test FastAPI client
│
├── scripts/
│   ├── run_ingestion.py                   ← CLI script to run data pipeline
│   │                                         - python scripts/run_ingestion.py --source all
│   │                                         - python scripts/run_ingestion.py --source devgan
│   │
│   └── verify_db.py                       ← CLI script to check ChromaDB contents
│                                             - Prints collection count, sample records
│                                             - Run after ingestion to verify
│
├── .env                                   ← Local dev secrets (gitignored)
├── .env.example                           ← Template for new developers
│                                             GROQ_API_KEY=
│                                             SUPABASE_URL=
│                                             SUPABASE_KEY=
│                                             CHROMA_PERSIST_DIR=./data/chroma
│                                             ALLOWED_ORIGINS=http://localhost:5173
│                                             ADMIN_API_KEY=
│
├── Dockerfile                             ← Production Docker image for Render
├── docker-compose.yml                     ← Local development (FastAPI + optional services)
│                                             services: backend (port 8000)
│
├── requirements.txt                       ← All Python dependencies (pinned versions)
├── pytest.ini                             ← Pytest config (testpaths, asyncio mode)
└── .gitignore
```

---

## `.github/workflows/deploy.yml` — CI/CD

```
.github/
└── workflows/
    └── deploy.yml                         ← GitHub Actions CI/CD
                                              - Triggers on push to main
                                              - Job 1: Run backend tests (pytest)
                                              - Job 2: Run frontend lint (eslint)
                                              - Vercel auto-deploys frontend from GitHub
                                              - Render auto-deploys backend from GitHub
                                              - No manual deploy steps needed after initial setup
```

---

## Supabase Database Schema

```sql
-- Run this in Supabase SQL editor to set up the sessions table

CREATE TABLE sessions (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id  TEXT NOT NULL,
  role        TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
  content     TEXT NOT NULL,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast session lookups
CREATE INDEX idx_sessions_session_id ON sessions(session_id);
CREATE INDEX idx_sessions_created_at ON sessions(created_at);

-- Auto-delete sessions older than 30 days (run as cron or use pg_cron extension)
-- DELETE FROM sessions WHERE created_at < NOW() - INTERVAL '30 days';

-- Enable Row Level Security (required by Supabase)
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
```

---

## Implementation Order (Recommended)

Follow this order to build the MVP with zero blocked dependencies:

```
Phase 1 — Data Foundation (Day 1-2)
  ✅ backend/scrapers/pipeline.py         ← Run ingestion first; need data in ChromaDB before testing RAG
  ✅ backend/scrapers/sources/devgan.py   ← Start with Devgan.in (cleanest IPC HTML data)
  ✅ backend/app/db/vector_store.py       ← ChromaDB setup
  ✅ backend/app/utils/embedder.py        ← Embedding model loader
  ✅ scripts/run_ingestion.py             ← Verify data is in ChromaDB

Phase 2 — RAG Core (Day 3-4)
  ✅ backend/app/utils/bm25_index.py      ← BM25 keyword search
  ✅ backend/app/utils/rrf.py             ← Re-ranking
  ✅ backend/app/utils/prompt_builder.py  ← Prompt assembly
  ✅ backend/app/services/groq_client.py  ← LLM streaming
  ✅ backend/app/services/rag_engine.py   ← Wire it all together
  ✅ backend/tests/test_rag_engine.py     ← Test retrieval quality

Phase 3 — API Layer (Day 5)
  ✅ backend/app/core/config.py
  ✅ backend/app/models/schemas.py
  ✅ backend/app/api/routes.py
  ✅ backend/app/main.py
  ✅ backend/app/db/session_store.py      ← Supabase connection
  ✅ backend/tests/test_routes.py

Phase 4 — Agent Layer (Day 6-7)
  ✅ backend/app/agents/state.py
  ✅ backend/app/agents/nodes/*.py        ← All 5 nodes
  ✅ backend/app/agents/graph.py
  ✅ backend/app/services/agent_runner.py
  ✅ backend/app/services/query_classifier.py

Phase 5 — Frontend (Day 8-9)
  ✅ frontend/src/api/chatApi.js          ← Wire to backend first
  ✅ frontend/src/hooks/useSession.js
  ✅ frontend/src/hooks/useChat.js
  ✅ frontend/src/store/chatStore.js
  ✅ frontend/src/components/InputBar.jsx
  ✅ frontend/src/components/ChatWindow.jsx
  ✅ frontend/src/components/MessageBubble.jsx
  ✅ frontend/src/components/LegalDisclaimer.jsx
  ✅ frontend/src/App.jsx

Phase 6 — Deployment (Day 10)
  ✅ backend/Dockerfile
  ✅ backend/.env.example
  ✅ frontend/vercel.json
  ✅ .github/workflows/deploy.yml
  ✅ Connect GitHub → Vercel (frontend)
  ✅ Connect GitHub → Render (backend)
  ✅ Add env vars in Render + Vercel dashboards
```

---

## Quick-Start Commands

```bash
# ── BACKEND ──────────────────────────────────────────────────

# Clone and setup
cd backend
python -m venv venv
source .venv/Scripts/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium       # For scraping

# Copy and fill environment variables
cp .env.example .env

# Step 1: Run data ingestion (downloads and indexes legal data)
python scripts/run_ingestion.py --source devgan
python scripts/run_ingestion.py --source indiacode
python scripts/verify_db.py       # Confirm data is in ChromaDB

# Step 2: Start FastAPI server
uvicorn app.main:app --reload --port 8000

# Step 3: Run tests
pytest tests/ -v

# ── FRONTEND ──────────────────────────────────────────────────

cd frontend
npm install

# Copy and set backend URL
cp .env.example .env              # Set VITE_API_URL=http://localhost:8000

# Start dev server
npm run dev                       # Opens at http://localhost:5173

# Build for production
npm run build

# ── DOCKER (local full stack) ─────────────────────────────────

cd backend
docker build -t legal-ai-backend .
docker run -p 8000:8000 --env-file .env legal-ai-backend
```

---

*File: folder-structure.md — version 1.0*
*This document is the authoritative source for project structure. Any new file must be added here with a description before being created.*

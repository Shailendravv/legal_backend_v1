# Indian Legal AI Chatbot — Complete Architecture (HDL + LDL)

> **Document Purpose:** This file is written for both humans and AI agents.
> Every section is structured so a developer can implement it directly, and an AI coding assistant can use it as a precise specification with zero ambiguity.
>
> **Product:** AI-powered legal chatbot for Indian law (starting with IPC — Indian Penal Code and BNS — Bharatiya Nyaya Sanhita).
> **Stack:** React (frontend) · FastAPI + Python (backend + AI) · Groq LLM · Qdrant Cloud · LangGraph
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

A user types a legal question in English (e.g. "What is Section 302 IPC?" or "My neighbor stole my bike and threatened me — what can I do?"). The system retrieves accurate, grounded answers from real Indian legal documents and streams the response back in real time. Every answer cites the exact IPC or BNS section it came from.

### Core design philosophy

- **Hybrid RAG first, Agents when needed.** Simple queries use a fast RAG pipeline. Complex multi-act or scenario-based queries escalate to a LangGraph agent.
- **Grounding over generation.** The LLM is instructed to answer ONLY from retrieved legal text. If information is not in the retrieved context, the system says so.
- **Section-level chunking.** Legal documents are never split by character count. Each IPC/BNS section is its own retrieval unit.
- **IPC to BNS Transition Support.** The system explicitly maps old IPC sections to their new BNS (2023) equivalents to help users navigate the legal transition.
- **Zero paid APIs.** Groq free tier, Qdrant Cloud free tier, HuggingFace free models, Render/Vercel free hosting.

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
        │        QDRANT CLOUD (Managed)               │
        │  Vector store · Metadata filter · Hybrid    │
        │  (Persistent free tier - no data loss)      │
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
  → Cleaner → Section Chunker → Metadata Tagger (IPC-BNS mapping)
  → BAAI/bge-small-en-v1.5 Embedder → Qdrant Cloud Upsert

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
| **Vector DB** | Qdrant Cloud | Persistent free tier (1GB), native hybrid search, superior filtering |
| **Agent framework** | LangGraph | Stateful multi-step graphs, native LangChain interop |
| **Backend** | FastAPI (Python 3.11) | Async, StreamingResponse, Pydantic validation |
| **Frontend** | React + Vite | Fast, component-based, easy SSE integration |
| **UI library** | Shadcn/UI + Tailwind CSS | Professional legal-tech aesthetic, free |
| **Session store** | Supabase (free PostgreSQL) | Managed, free 500MB, JSONB for conversation history |
| **Frontend deploy** | Vercel | Global CDN, zero-config, free |
| **Backend deploy** | Render | Free Web Service, Docker support |
| **Scraping** | Playwright (Python) | Handles JS-rendered government sites|
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
[Step 5] Metadata Tagger (IPC-BNS Mapping)
    - Attach structured metadata: act, section, title, category.
    - NEW: Add `equivalent_section_id` (e.g. IPC-302 maps to BNS-101-01).
    │
    ▼
[Step 6] Embedder
    - Model: BAAI/bge-small-en-v1.5 (sentence-transformers)
    - Instruction prefix: "Represent this legal passage for retrieval: "
    - Output: 384-dimensional float32 vector
    │
    ▼
[Step 7] Qdrant Cloud Upsert
    - Collection: "indian_legal_docs"
    - Upsert by chunk_id (idempotent — safe to re-run)
```

### 5.2 Chunk JSON schema

Every chunk stored in Qdrant must conform to this exact schema:

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
  "year":       1860,
  "equivalent_section": "BNS-318-01"
}
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
    - If yes → add Qdrant `must` filter for `act`.
    - If query contains "Section NNN" → add `must` filter for `section`.
    │
    ▼
[Step 3] Parallel Hybrid Search
    - Qdrant native hybrid search (Vector + Sparse).
    - If sparse not available: manual RRF between Vector Search and BM25.
    │
    ▼
[Step 4] RRF Re-ranking (Reciprocal Rank Fusion)
    - Merge vector rank list + BM25 rank list
    - score = 1/(k + rank_vector) + 1/(k + rank_bm25)  [k=60]
    - Select top 5 chunks by merged score
    │
    ▼
[Step 5] Context Builder & Mapping Layer
    - If retrieved chunk is IPC, check if its BNS equivalent is already in context.
    - If not, proactively add the equivalent BNS section summary to the context.
    - Format: "Section {section}, {act} ({year}): {content}"
    │
    ▼
[Step 6] Prompt Builder
    - Inject system prompt with IPC-BNS transition instruction.
    - Inject retrieved context + conversation history.
    │
    ▼
[Step 7] Groq LLM Inference (stream=True)
```

### 6.2 System prompt template

```
SYSTEM PROMPT:
You are a Senior Legal Assistant specializing in Indian criminal and civil law.
You provide information on the Indian Penal Code (IPC) and its modern replacement, the Bharatiya Nyaya Sanhita (BNS).

STRICT RULES — follow these without exception:
1. Answer ONLY using the legal sections provided in CONTEXT below.
2. Every factual claim MUST be followed by its citation: [Section X, IPC] or [Section X, BNS].
3. For IPC queries, whenever possible, also mention the equivalent BNS section if it exists in the CONTEXT.
4. If the answer cannot be found in the provided context, respond exactly:
   "I don't have sufficient information in my knowledge base to answer this accurately.
    Please consult a qualified advocate."
5. Never fabricate section numbers, punishments, or legal interpretations.
6. Use plain English. Avoid unnecessary legal jargon unless quoting a statute directly.
7. Always end your response with the Mandatory Disclaimer.
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

### 7.2 LangGraph node design

- **[Node 1: Query Analyser]**: Classify intent (factual/scenario/comparison) and extract entities.
- **[Node 2: Act Router]**: Map to act-specific filters (IPC vs BNS).
- **[Node 3: Parallel Retriever]**: Execute hybrid search for each act in parallel.
- **[Node 4: Fact-Checker & Mapper]**: Verify consistency between retrieved sections and ensure IPC-BNS mapping is complete.
- **[Node 5: Response Synthesiser]**: Build response using Groq LLM.

---

## 8. Vector Database (LDL)

### 8.1 Why Qdrant Cloud?

| Database | Persistence | Hybrid Search | Pros |
|---|---|---|---|
| **ChromaDB** | Ephemeral (Render) | Needs Manual BM25 | In-process, simple for development. |
| **Qdrant Cloud** | Persistent | Native | Managed, free 1GB tier, high performance, structured filtering. |

### 8.2 Qdrant collection configuration

```python
from qdrant_client import QdrantClient
from qdrant_client.http import models

client = QdrantClient(url="...", api_key="...")

# Create collection
client.create_collection(
    collection_name="indian_legal_docs",
    vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
    sparse_vectors_config={
        "text": models.SparseVectorParams(index=models.SparseIndexParams(on_disk=True))
    }
)

# Search with metadata filter
client.search(
    collection_name="indian_legal_docs",
    query_vector=embed_query(user_query),
    query_filter=models.Filter(
        must=[models.FieldCondition(key="act", match=models.MatchValue(value="IPC"))]
    )
)
```

---

## 9. FastAPI Backend (LDL)

### 9.1 API routes

- `POST /chat`: Main chat endpoint — returns SSE stream.
- `GET /history/{session_id}`: Get last N conversation turns from Supabase.
- `DELETE /session/{session_id}`: Clear user session.
- `POST /ingest`: Trigger offline ingestion (protected by API key).
- `GET /health`: Health check for Render.

---

## 10. React Frontend (LDL)

### 10.1 Key components

- **ChatWindow**: Message list with auto-scroll.
- **MessageBubble**: Styling for AI vs User, Markdown rendering, Citation chips.
- **CitationCard**: Expandable panel showing raw legal text.
- **LegalDisclaimer**: Persistent banner and auto-appended response text.
- **IPC_BNS_Toggle**: (Optional) UI switch to explicitly prefer old/new laws.

---

## 11. Deployment Strategy

### 11.1 Platform allocation

- **Frontend**: Vercel (Global CDN).
- **Backend**: Render (Docker web service).
- **Session DB**: Supabase (PostgreSQL).
- **Vector DB**: Qdrant Cloud (Managed persistent store).
- **LLM**: Groq (Free API).

---

## 12. Security and Compliance

### 12.1 Hallucination mitigation layers

- **Prompt**: "Answer ONLY from provided context."
- **Retrieval**: Hybrid search + metadata filter reduces irrelevant context.
- **Post-generation**: Self-RAG verification before streaming.
- **UI**: Every answer shows collapsible "Sources" panel.
- **Fallback**: Scripted "I don't know" if no relevant law is found.

### 12.2 Mandatory legal disclaimer
Must appear in persistent banner and at the end of every response:
> ⚠ Disclaimer: This AI legal assistant provides information for educational purposes only. It does not constitute legal advice. For any legal matter, consult a qualified advocate or legal professional registered with the Bar Council of India.

---

## 13. Future Improvements

| Improvement | Effort | Impact |
|---|---|---|
| **Multilingual support** | Medium | Swap embedding to BGE-M3 (supports Hindi/regional languages). |
| **Clickable legal citations**| Low | Deep-links to indiacode.nic.in. |
| **Case law integration** | High | Add judgments from IndianKanoon. |
| **BNSS/BSA integration**| Medium | Add procedural and evidence law updates. |
| **Admin dashboard** | Medium | Monitor hallucinations and query trends. |

---

*Document version: 1.1 — Updated for Qdrant Cloud and IPC-BNS mapping.*

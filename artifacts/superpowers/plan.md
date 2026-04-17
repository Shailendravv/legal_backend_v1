# Implementation Plan: Unified Ingestion Architecture & Resilience

## Goal
Implement the Unified Ingestion Architecture as proposed in `docs/Ingestion_Pipeline_Readiness_Report.md`. This includes decoupling the crawler via a Source Orchestrator, enhancing the extractor for multi-source support, and hardening the Playwright crawler with production-grade resilience.

## Current State
- `/chat` endpoint is tightly coupled to `PlaywrightCrawler`.
- Crawler lacks full stealth and header rotation.
- Extractor is functional but needs broader source support.

## Implementation Details

### 1. Source Orchestrator (`app/pipeline/orchestrator.py`)
- Define `SourceOrchestrator` to dispatch tasks based on source type.
- Supported types: `web` (via Playwright), `local` (files), `dataset` (HF/Kaggle).

### 2. Extractor Enhancements (`app/pipeline/extractor.py`)
- Standardize the `RawContent` object.
- Add skeletons for Parquet/CSV and PDF handlers.

### 3. Crawler Resilience (`app/crawler/playwright_crawler.py`)
- Integrate `playwright-stealth`.
- Implement dynamic User-Agent rotation.
- Add disk caching at `.crawler_cache/`.

### 4. API Redesign (`app/api/v1/endpoints/chat.py`)
- Route all requests through the `SourceOrchestrator`.
- Expand response to show metadata about the ingestion strategy and source.

## Steps

1. **Step 1: Create Source Orchestrator**
   - Implement `app/pipeline/orchestrator.py`.
   - *Verification*: Unit test or script to confirm routing logic.

2. **Step 2: Install Dependencies**
   - Run `pip install playwright-stealth fake-useragent`.
   - *Verification*: `pip list | Select-String "playwright-stealth"`

3. **Step 3: Harden Crawler (Resilience)**
   - Update `PlaywrightCrawler` with stealth and header rotation.
   - *Verification*: Log check for stealth activation.

4. **Step 4: Implement Ingestion Cache**
   - Add file-based caching to `PlaywrightCrawler`.
   - *Verification*: Run twice, verify second hit is from cache.

5. **Step 5: Update Content Extractor**
   - Refactor to handle multi-source outputs.
   - *Verification*: Ensure existing tests still pass.

6. **Step 6: Final API Integration & /chat Response**
   - Refactor `/chat` to use orchestrator.
   - Ensure the response contains all debugging info specified in the report and user request.
   - *Verification*: API call to `/chat` with a query like "IPC 302".

## Verification
- Logs must show `[ORCHESTRATOR] Routing to: WebCrawler`.
- Logs must show `[CACHE HIT]` or `[NETWORK FETCH]`.
- API response must include `source_strategy`, `resolved_act`, and `pii_flags`.

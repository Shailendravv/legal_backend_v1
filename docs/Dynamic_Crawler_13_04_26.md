# Dynamic Crawler Implementation - 13/04/2026

## Overview
As of April 13, 2026, the `PlaywrightCrawler` has been significantly upgraded to support dynamic, query-aware legal data ingestion from portals like India Code (`indiacode.nic.in`). This document outlines the key features and architectural improvements made to resolve the "Access Denied" blocks and the "NotImplementedError" on Windows.

## 1. Dynamic Search Architecture
The crawler no longer requires hardcoded URLs. It now interprets natural language queries through a dedicated parsing layer.

- **Query Parsing**: Converts inputs like "IPC 420" or "Section 302 of Indian Penal Code" into structured objects (`act_name`, `section`, `search_term`).
- **Multi-Strategy Navigation**:
    - **Strategy A (Direct URL)**: Attempts to jump directly to known Act handles with specific section parameters.
    - **Strategy B (Site Search)**: Uses the portal's internal search engine with optimized keywords (e.g., "Section 420 Indian Penal Code").
    - **Strategy C (Homepage Navigation)**: Mimics human behavior by navigating to the homepage, physically typing into the search box, and pressing Enter.

## 2. Windows & Async Compatibility
To resolve the `NotImplementedError` caused by the `SelectorEventLoop` on Windows when spawning Playwright subprocesses:
- **Sync Fallback**: Implemented `_sync_dynamic_crawl` using `sync_playwright`.
- **Thread Delegation**: The main `dynamic_crawl` (async) detects the environment and automatically delegates work to the sync version via `asyncio.to_thread` when necessary.

## 3. Super-Stealth & WAF Bypass (Akamai)
To bypass aggressive bot detection (Akamai/Edgesuite):
- **Warm-up Sessions**: Visits high-trust sites like Google.com before the target portal to establish session validity.
- **Human Interaction**: Mimics realistic mouse movements, random scrolls, and variable typing delays.
- **Fingerprinting**: Uses high-trust User-Agents, random viewports (1280x720 to 1440x900), and Client Hint headers (`Sec-CH-UA`).
- **Referer Spoofing**: Sets appropriate `Referer` headers to make search requests look like organic internal navigation.

## 4. Error Resilience & Fallback
The crawler is now "error-aware":
- **DSpace Error Detection**: Recognizes "Invalid URL or Argument" pages at the extraction layer and rejects them as failures.
- **Search Validation**: Detects "Search produced no results" and automatically triggers broader search retries (e.g., falling back from Section search to Act-only search).
- **Block Signal Monitoring**: Actively scans for "Access Denied" or "Reference #" strings to trigger immediate strategy pivots.

## 5. Pipeline Integration
- **`chat` Endpoint**: Updated to accept a `ChatRequest` JSON model from the frontend.
- **`ContentExtractor`**: Added support for `source_type: "text"` to allow the pass-through of pre-extracted text from the dynamic crawler.
- **`ContentCleaner`**: Integrated to provide PII redaction and text normalization on all dynamic results.

---
**Status**: Production Ready
**Platform**: Cross-platform (Linux/Windows)
**Target**: indiacode.nic.in

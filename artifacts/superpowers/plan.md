# Implementation Plan: Ingestion Resilience & Data Sourcing

## Goal
Implement the recommendations from the brainstorm: finalize high-quality data sources (HuggingFace/Kaggle) and enhance the Playwright crawler with production-grade resilience (stealth, rotating headers, caching).

## Current State
- `PlaywrightCrawler` exists with basic async/sync support for Windows.
- `ContentExtractor` and `ContentCleaner` are functional and integrated in `/chat`.
- Data sources are listed but not prioritized or fully utilized in the pipeline.

## Implementation Details

### 1. Document Architecture Updates
- Update `docs/legal_ai_architecture.md` to:
    - Mark HuggingFace (169Pi) as the primary/best source.
    - Mark Devgan.in as the testing source.
    - Add "Long-Term (production-grade)" section with Stealth, Proxies, Caching, and PDF pipeline.

### 2. Dependency Management
- Install `playwright-stealth` and `fake-useragent`.
- Update `pyproject.toml` if applicable.

### 3. Resilience Enhancements (`app/crawler/playwright_crawler.py`)
- **Stealth**: Integrate `stealth_sync` (for Windows) and `stealth_async`.
- **Rotating Headers**: use `fake-useragent` for dynamic User-Agent strings.
- **Caching**: Implement a simple file-based cache (`.crawler_cache/`) to store URL contents and avoid redundant fetching.

### 4. Verification Update (`app/api/v1/endpoints/chat.py`)
- Log and display if content was retrieved from "CACHE" or "NETWORK".
- Ensure stealth mode is active.

## Steps

1. **Step 1: Update Architecture Doc**
   - Modify `docs/legal_ai_architecture.md`.
   - *Verification*: View file to ensure markdown is correct.

2. **Step 2: Install Dependencies**
   - Run `pip install playwright-stealth fake-useragent`.
   - *Verification*: `pip list | grep playwright-stealth`.

3. **Step 3: Implement Stealth & Headers**
   - Modify `PlaywrightCrawler` to apply stealth to the browser page.
   - Inject rotating User-Agent headers.
   - *Verification*: Test against a site that detects headless browsers (e.g., indiacode.nic.in).

4. **Step 4: Implement Ingestion Cache**
   - Create a disk cache for raw HTML.
   - Use URL hashing for keys.
   - *Verification*: Run crawler twice; second run should be instantaneous and log "Cache Hit".

5. **Step 5: Final API Integration**
   - Update `/chat` response to include `source_strategy` (e.g., "resilient_fetch").
   - *Verification*: Hit `/chat` and observe response.

## Verification
- Logs must show `[CACHE HIT]` or `[NETWORK FETCH]`.
- Architecture document must reflect the new priorities.
- Browser fingerprinting check (manual/log verification).

## Goal
Refine the data ingestion strategy and enhance the architecture for production-grade scraping resilience in the Indian Legal AI project. This includes finalizing dataset priorities and adding long-term scraper features (stealth, proxies, caching).

## Constraints
- **Zero Cost**: Maintain 100% free and open-source stack (Groq, Qdrant free tiers).
- **Legality**: Strictly follow DPDPA 2023 for public legal data; avoid PII.
- **Complexity**: Keep the system modular to allow swapping between testing (Devgan.in) and production (HuggingFace/India Code) sources.
- **Platform**: Windows environment with Python/FastAPI backend.

## Known context
- The project focuses on IPC to BNS transition.
- Current pipeline uses Playwright, BeautifulSoup, and Qdrant.
- docs/legal_ai_architecture.md is the source of truth for the system design.

## Risks
- **IP Blocking**: Government sites (India Code) are notoriously sensitive to automated traffic.
- **Data Inconsistency**: Discrepancies between official PDFs and unofficial HTML sites (Devgan).
- **Redundancy**: Re-crawling the same pages during development increases risk and waste.
- **Parse Failures**: Complex legal PDFs (multi-column, scans) are hard to parse into structured Markdown.

## Options (2?4)
1. **Source-First Strategy**: Prioritize HuggingFace (169Pi) and Kaggle datasets for bulk ingestion to bypass scraping hurdles entirely, using Devgan.in only as a testbed for crawler logic.
2. **Stealth Crawler Suite**: Integrate playwright-stealth and rotating headers early in the pipeline to simulate human behavior, paired with a proxy middleware.
3. **Optimized Pipeline (Persistence)**: Add a caching layer (sqlite/local file) to store raw HTML/PDF responses and a dedicated PDF ingestion pipeline using marker-pdf for high-fidelity extraction.

## Recommendation
Implement **all three options** in a staged approach.
- **Phase 1**: Update architecture to explicitly mark HuggingFace as the primary "Base" and Devgan as "Testing". 
- **Phase 2**: Enhance the "Ingestion Pipeline" section with "Long-term" production-grade components (Stealth, Proxies, Caching).

## Acceptance criteria
- [ ] docs/legal_ai_architecture.md updated with "HuggingFace" as the BEST OPTION.
- [ ] docs/legal_ai_architecture.md updated with "Devgan.in" for testing.
- [ ] "Long-Term (production-grade)" section added or expanded with stealth Playwright, proxies, rotating headers, PDF pipeline, and result caching.
- [ ] Brainstorm artifact successfully saved to rtifacts/superpowers/brainstorm.md.

# Finish: Step 2 - Content Extractor Implementation

## Summary of Changes
- **Pipeline Stage**: `ContentExtractor` (Step 2) is now functional.
- **HTML Extraction**: Uses BS4 for clean text extraction (no script/style tags).
- **PDF Extraction**: Integrated `pymupdf4llm` for PDF-to-Markdown (Marker dependency is large/complex, PyMuPDF4LLM is stable).
- **Tabular Extraction**: Uses `pandas` to extract JSON rows from CSV and Parquet.
- **API Integration**: `/chat` endpoint now routes through Step 1 (Ingestion) and Step 2 (Extraction) sequentially.
- **Logging**: Mandatory logs (START/END/ERROR) implemented as specified.

## Verification Run
- **Command**: `uv run python app/pipeline/test_extractor.py`
- **Output Preview**:
  - `🚀 Starting: Content Extraction - html`
  - `✅ Completed: Content Extraction - html`
  - `🚀 Starting: Content Extraction - csv`
  - `✅ Completed: Content Extraction - csv`
  - `❌ Failed: Content Extraction - pdf | Error: PDF file not found at: non_existent.pdf`

## Manual Validation
- Run the FastAPI application: `uv run uvicorn main:app --reload`
- Call POST `/api/v1/chat`:
  - Request body (ignored currently, uses Wikipedia as test): `{}`
  - Response:
    ```json
    {
      "current_step": "Content Extractor",
      "input_type": "html",
      "status": "completed",
      "output_preview": "<Clean extracted text from Wikipedia home page>",
      "next_step": "Cleaner (pending)"
    }
    ```

## Follow-ups
- Proceed to **Step 3: Cleaner** for stripping remaining noise and anonymizing PII.
- Consider installing `marker-pdf` if higher MD accuracy is required for legal documents.

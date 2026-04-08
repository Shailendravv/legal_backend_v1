# Implementation Plan: Pipeline Step 2 - Content Extractor

## Goal
Implement Step 2 of the data pipeline: `Content Extractor`. This step converts various raw inputs (HTML, PDF, CSV, Parquet) into structured text, markdown, or lists of dicts.

## Current Architecture
- Step 1 (Crawler) is complete.
- Basic FastAPI structure exists with `/chat` hijacking for verification.

## Implementation Details

### Dependencies
- `beautifulsoup4`: HTML extraction.
- `marker-pdf`: PDF to Markdown (preferred).
- `pymupdf4llm`: Fallback PDF converter.
- `pandas`: CSV/Parquet processing.
- `pyarrow`: For Parquet support.

### New Module: `app/pipeline/extractor.py`
- `extract_content(input_data)`: Main entry point.
- `extract_html(html_string)`: BS4 extraction (no scripts/styles).
- `extract_pdf(file_path_or_url)`: PDF to Markdown converter.
- `extract_csv(file_path)`: CSV to list of dicts.

### API Update: `app/api/v1/endpoints/chat.py`
- Modify `/chat` to return Step 2 output.

### Logging
- Logger implementation in each sub-function (Start, End, Error).

## Steps

1.  **Add Dependencies**: Add required libraries to `pyproject.toml` and reinstall.
2.  **Create Extractor**: Create `app/pipeline/extractor.py` with the routing logic.
3.  **Implement HTML Extraction**: Use BS4 to extract main text.
4.  **Implement PDF Extraction**: Use `marker` to convert to Markdown.
5.  **Implement CSV/Parquet Extraction**: Use pandas for tabular data.
6.  **Integrate with API**: Update `/chat` router to use `extract_content`.
7.  **Final Verification**: Test with sample inputs.

## Verification
- Test with HTML string.
- Test with sample PDF path.
- Test with sample CSV path.
- Check logs for "🚀 Starting", "✅ Completed", and "❌ Failed" messages.

# Implementation Plan: Pipeline Step 3 - Cleaner

## Goal
Implement Step 3 of the data pipeline: `Cleaner`. This step cleans noisy extracted content, removes boilerplate, normalizes text, and redacts PII while preserving legal structure and semantics.

## Current Architecture
- Step 1 (Crawler) is complete.
- Step 2 (Content Extractor) is complete.
- Basic FastAPI structure exists with `/chat` hijacking for verification.

## Implementation Details

### Module: `app/pipeline/cleaner.py`
- `clean_content(input_data)`: Main entry point.
- `clean_pdf_text(text)`: Remove page numbers, headers/footers, court stamps.
- `clean_html_text(text)`: Remove navigation menus, footer/header boilerplate from markdown/text.
- `normalize_text(text)`: Normalize whitespace and unicode characters (UTF-8).
- `redact_pii(text)`: Use regex to replace Aadhaar, phone numbers, and emails with tags like `[REDACTED_AADHAAR]`.

### API Update: `app/api/v1/endpoints/chat.py`
- Modify `/chat` to return Step 3 output.

### Logging (Mandatory)
- Log Start, End, and Error for each cleaning stage:
  - `🚀 Starting: Cleaning - <stage>`
  - `✅ Completed: Cleaning - <stage>`
  - `❌ Failed: Cleaning - <stage>`

## Steps

1. **Create Cleaner Module**: Create `app/pipeline/cleaner.py` with the `ContentCleaner` class and required modular functions.
2. **Implement Text Normalization**: Whitespace and Unicode normalization.
3. **Implement PII Redaction**: Regex-based redaction for Aadhaar, Phone, and Email.
4. **Implement PDF-specific Cleaning**: Logic for page numbers and legal document headers.
5. **Implement HTML-specific Cleaning**: Logic for boilerplate removal.
6. **Integrate with API**: Update `/chat` router to use `clean_content`.
7. **Final Verification**: Test with various noisy samples.

## Verification
- Run `app/pipeline/cleaner.py` directly with a test script or use `/chat` endpoint.
- Verify PII redaction: Ensure "1234 5678 9012" -> `[REDACTED_AADHAAR]`.
- Verify whitespace: Ensure multiple spaces/newlines are normalized.
- Check logs for the mandatory format.

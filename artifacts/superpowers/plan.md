# Implementation Plan: Source Handlers (Local & HF)

## Goal
Implement real `HuggingFaceHandler` and `LocalFileHandler` for the `SourceOrchestrator` to move away from mocked responses.

## Current State
- `SourceOrchestrator` mocks `HF:` and local file paths.
- `ContentExtractor` exists and can handle some file types but expects paths/content in a specific way.
- `datasets` library (HuggingFace) is missing.

## Steps

1. **Step 1: Install Dependencies**
   - Install `datasets` for HuggingFace support.
   - *Verification*: `pip show datasets`

2. **Step 2: Implement Base Handler & LocalFileHandler**
   - Create `app/pipeline/handlers.py`.
   - Implement `LocalFileHandler` for reading `.pdf`, `.csv`, `.parquet`, and `.txt` files.
   - *Verification*: Unit test reading a sample file.

3. **Step 3: Implement HuggingFaceHandler**
   - Implement `HuggingFaceHandler` in `app/pipeline/handlers.py`.
   - Support `hf:dataset_name` loading.
   - *Verification*: Script to load a small sample dataset (e.g., `tiny_shakespeare`).

4. **Step 4: Update SourceOrchestrator**
   - Integrate the real handlers into `app/pipeline/orchestrator.py`.
   - *Verification*: Verify routing logic points to these handlers.

5. **Step 5: Final Verification**
   - End-to-end test via `scratch/test_pipeline_handlers.py`.

## Verification
- `[ORCHESTRATOR] Strategy: LocalFile` must return real content.
- `[ORCHESTRATOR] Strategy: HuggingFace` must return real dataset content.
- All errors (file not found, dataset not found) must be logged and handled gracefully.

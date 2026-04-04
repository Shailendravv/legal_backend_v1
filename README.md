# Legal Backend

This is the backend service for the Legal Project.

## Getting Started

Follow the steps below to set up your development environment and start the project.

### Setup and Start

```bash
uv init
uv venv
source .venv/Scripts/activate
uv add -r requirements.txt
uv run uvicorn main:app --reload
```

## Features

- Built with FastAPI
- Managed with [uv](https://docs.astral.sh/uv/) for high-performance dependency management and packaging.

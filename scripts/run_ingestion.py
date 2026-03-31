import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to sys.path so we can import 'app' and 'scrapers'
sys.path.append(str(Path(__file__).resolve().parent.parent))

from scrapers.pipeline import pipeline
from app.core.logger import setup_logger
from app.core.config import settings
from app.core.logger import logger

async def main():
    """
    Main entry point for manual ingestion.
    Usage: python scripts/run_ingestion.py --source devgan
    """
    # Initialize Logger
    setup_logger()

    # Log environment info (don't log secrets)
    logger.info(f"Ingestion started in environment: {settings.LOG_LEVEL}")
    logger.info(f"ChromaDB path: {settings.CHROMA_PERSIST_DIR}")

    # Check for arguments
    source = "all"
    if "--source" in sys.argv:
        idx = sys.argv.index("--source")
        if idx + 1 < len(sys.argv):
            source = sys.argv[idx + 1]

    # Run the master pipeline
    logger.info(f"Triggering ingestion for source: {source}")
    await pipeline.run_full_pipeline()
    logger.info("Ingestion script completed successfully.")

if __name__ == "__main__":
    asyncio.run(main())


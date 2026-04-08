import asyncio
import os
import pandas as pd
from typing import Any, Dict, List, Optional, Union
from bs4 import BeautifulSoup
import pymupdf4llm
from app.core.logger import logger
from app.pipeline.base import Stage

class ContentExtractor(Stage):
    """
    Step 2: Content Extractor
    Converts raw HTML, PDF, or CSV/Parquet into structured text/markdown/rows.
    """

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs the extraction based on the input source type.
        Expected input: { "source_type": "html|pdf|csv|parquet", "content": "..." }
        """
        source_type = input_data.get("source_type", "").lower()
        content = input_data.get("content")

        logger.info(f"🚀 Starting: Content Extraction - {source_type}")

        try:
            if source_type == "html":
                extracted_content = self.extract_html(content)
            elif source_type == "pdf":
                extracted_content = self.extract_pdf(content)
            elif source_type in ["csv", "parquet"]:
                extracted_content = self.extract_tabular(content, source_type)
            else:
                raise ValueError(f"Unsupported source type: {source_type}")

            logger.info(f"✅ Completed: Content Extraction - {source_type}")
            return {
                "current_step": "Content Extractor",
                "input_type": source_type,
                "status": "completed",
                "extracted_content": extracted_content
            }
        except Exception as e:
            logger.error(f"❌ Failed: Content Extraction - {source_type} | Error: {str(e)}")
            return {
                "current_step": "Content Extractor",
                "input_type": source_type,
                "status": "failed",
                "error": str(e)
            }

    def extract_html(self, html_content: str) -> str:
        """Extracts meaningful text from HTML, removing scripts and styles."""
        if not html_content:
            return ""
        
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Remove unwanted tags
        for script_or_style in soup(["script", "style", "nav", "footer", "header"]):
            script_or_style.decompose()
            
        # Get text and clean up whitespace
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)

    def extract_pdf(self, pdf_path: str) -> str:
        """
        Extracts Markdown from PDF using PyMuPDF4LLM (fallback).
        Note: Marker preferred if available, but staying with PyMuPDF4LLM for stability.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found at: {pdf_path}")
            
        # PyMuPDF4LLM directly converts to Markdown
        md_text = pymupdf4llm.to_markdown(pdf_path)
        return md_text

    def extract_tabular(self, file_path: str, file_type: str) -> List[Dict[str, Any]]:
        """Extracts rows from CSV or Parquet as a list of dicts."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{file_type.upper()} file not found at: {file_path}")

        if file_type == "csv":
            df = pd.read_csv(file_path)
        elif file_type == "parquet":
            df = pd.read_parquet(file_path)
        else:
            raise ValueError(f"Unsupported tabular type: {file_type}")

        # Convert to list of dictionaries
        return df.to_dict(orient="records")

# Functional shorthand for independent testing
async def extract_content(input_data: Dict[str, Any]) -> Dict[str, Any]:
    extractor = ContentExtractor()
    return await extractor.run(input_data)

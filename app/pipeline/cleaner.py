import re
import unicodedata
import json
from typing import Any, Dict, Optional, Union, List
from app.core.logger import logger
from app.pipeline.base import Stage

class ContentCleaner(Stage):
    """
    Step 3: Cleaner
    Cleans noisy extracted content, removes boilerplate, normalizes text, and redacts PII.
    """

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs the cleaning process.
        Expected input: { "type": "html|pdf|csv", "data": "<raw text OR markdown OR list of rows>" }
        """
        input_type = input_data.get("type", "").lower()
        data = input_data.get("data", "")

        if not data:
            logger.warning("⚠️ No data provided to Cleaner")
            return {
                "current_step": "Cleaner",
                "input_type": input_type,
                "status": "completed",
                "output_preview": "",
                "pii_flags": {"aadhaar": False, "phone": False, "email": False},
                "next_step": "Section Chunker (pending)"
            }

        logger.info(f"🚀 Starting: Cleaning - {input_type}")

        try:
            # 1. Tabular data handling (Conversion to text block)
            if isinstance(data, list):
                logger.info("📊 Cleaner: Converting list/tabular data to string for processing")
                # Convert list of dicts to a formatted JSON-like string for easier cleaning/redaction
                data = json.dumps(data, indent=2)

            # 2. Type-specific cleaning
            if input_type == "pdf":
                data = self.clean_pdf_text(data)
            elif input_type == "html":
                data = self.clean_html_text(data)
            
            # 3. Text Normalization (Mandatory for all types)
            data = self.normalize_text(data)

            # 3. PII Redaction
            data, pii_flags = self.redact_pii(data)

            logger.info(f"✅ Completed: Cleaning - {input_type}")
            
            return {
                "current_step": "Cleaner",
                "input_type": input_type,
                "status": "completed",
                "output_preview": data[:500],
                "pii_flags": pii_flags,
                "next_step": "Section Chunker (pending)",
                "cleaned_data": data
            }
        except Exception as e:
            logger.error(f"❌ Failed: Cleaning - {input_type} | Error: {str(e)}")
            return {
                "current_step": "Cleaner",
                "input_type": input_type,
                "status": "failed",
                "error": str(e)
            }

    def clean_pdf_text(self, text: str) -> str:
        """Remove page numbers, headers/footers, and legal document stamps."""
        logger.info("🚀 Starting: Cleaning - PDF structure")
        
        # Remove "Page X of Y" or "Page X"
        text = re.sub(r'(?i)Page \d+( of \d+)?', '', text)
        
        # Remove repetitive boilerplate like "Downloaded from...", "Date: ...", "Time: ..."
        # Note: Be careful not to remove actual legal dates.
        # This is a placeholder for more complex legal document header removal.
        
        # Remove common court stamps (placeholder regex)
        text = re.sub(r'\[STAMP:.*?\]', '', text)
        
        logger.info("✅ Completed: Cleaning - PDF structure")
        return text

    def clean_html_text(self, text: str) -> str:
        """Remove remaining HTML boilerplate or navigation text from markdown."""
        logger.info("🚀 Starting: Cleaning - HTML boilerplate")
        
        # If the extractor already did a good job, this might be minimal.
        # Removing common web UI elements that might have slipped through
        boilerplate_patterns = [
            r'Click here to.*',
            r'Sign in / Register',
            r'Privacy Policy \| Terms of Use',
            r'Copyright © \d{4}.*'
        ]
        for pattern in boilerplate_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            
        logger.info("✅ Completed: Cleaning - HTML boilerplate")
        return text

    def normalize_text(self, text: str) -> str:
        """Normalize whitespace and unicode characters."""
        logger.info("🚀 Starting: Cleaning - Normalization")
        
        # Unicode normalization (to NFKC - Compatible Decomposition, followed by Canonical Composition)
        text = unicodedata.normalize('NFKC', text)
        
        # Normalize whitespace
        text = re.sub(r'[ \t]+', ' ', text)  # multiple spaces/tabs to single space
        text = re.sub(r'\n{3,}', '\n\n', text)  # limit consecutive newlines to 2
        
        logger.info("✅ Completed: Cleaning - Normalization")
        return text.strip()

    def redact_pii(self, text: str) -> tuple[str, dict[str, bool]]:
        """Detect and redact PII like Aadhaar, Phone, and Email."""
        logger.info("🚀 Starting: Cleaning - PII Redaction")
        
        pii_flags = {
            "aadhaar": False,
            "phone": False,
            "email": False
        }

        # Aadhaar: 12 digits with optional spaces/hyphens
        aadhaar_pattern = r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
        if re.search(aadhaar_pattern, text):
            pii_flags["aadhaar"] = True
            text = re.sub(aadhaar_pattern, '[REDACTED_AADHAAR]', text)

        # Phone: Indian 10-digit mobile or with (+91)
        phone_pattern = r'(\+91[\s-]?)?[6-9]\d{9}\b'
        if re.search(phone_pattern, text):
            pii_flags["phone"] = True
            text = re.sub(phone_pattern, '[REDACTED_PHONE]', text)

        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.search(email_pattern, text):
            pii_flags["email"] = True
            text = re.sub(email_pattern, '[REDACTED_EMAIL]', text)

        # Summary flag
        pii_flags["pii_found"] = any(pii_flags.values())

        logger.info(f"✅ Completed: Cleaning - PII Redaction | PII Found: {pii_flags['pii_found']}")
        return text, pii_flags

# Functional shorthand for independent testing
async def clean_content(input_data: Dict[str, Any]) -> Dict[str, Any]:
    cleaner = ContentCleaner()
    return await cleaner.run(input_data)

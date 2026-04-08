import asyncio
from app.pipeline.cleaner import clean_content

async def test_cleaner():
    # 1. Test PDF-like text with headers/footers and PII
    pdf_input = {
        "type": "pdf",
        "data": """
        IN THE HIGH COURT OF KARNATAKA
        Page 1 of 10
        STAMP: [STAMP: CONFIDENTIAL]
        Case Number: 12345/2023
        Petitioner: John Doe
        Aadhaar: 1234 5678 9012
        Phone: +91 9876543210
        Email: lawyer@example.com
        
        The court has decided that...
        
        Page 2 of 10
        The decision persists...
        """
    }
    
    # 2. Test HTML noisy text
    html_input = {
        "type": "html",
        "data": "Click here to view more\nLegal Content Here\nCopyright © 2024 Legal Corp\nSign in / Register"
    }
    
    # 3. Test Text Normalization
    norm_input = {
        "type": "text",
        "data": "Extra   spaces    and\n\n\n\nToo many newlines."
    }

    print("--- Testing PDF Cleaning ---")
    pdf_result = await clean_content(pdf_input)
    print(f"PII Flags: {pdf_result['pii_flags']}")
    print(f"Cleaned Preview:\n{pdf_result['cleaned_data']}")
    
    print("\n--- Testing HTML Cleaning ---")
    html_result = await clean_content(html_input)
    print(f"Cleaned Preview:\n{html_result['cleaned_data']}")
    
    print("\n--- Testing Normalization ---")
    norm_result = await clean_content(norm_input)
    print(f"Cleaned Preview:\n{norm_result['cleaned_data']}")

if __name__ == "__main__":
    asyncio.run(test_cleaner())

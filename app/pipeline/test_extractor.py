import asyncio
import os
import pandas as pd
from app.core.logger import setup_logger, logger
from app.pipeline.extractor import extract_content

async def test_extractor():
    setup_logger()
    print("--- Test Content Extractor ---")
    
    # 1. HTML Test
    html_input = {
        "source_type": "html",
        "content": "<html><head><title>Test Title</title></head><body><style>p { color: red; }</style><h1>Main Content</h1><p>This is extracted text.</p><script>alert('Hidden');</script></body></html>"
    }
    html_res = await extract_content(html_input)
    print(f"\nHTML Extraction Status: {html_res['status']}")
    print(f"Content Preview: {html_res['extracted_content'][:100]}")

    # 2. CSV Test
    csv_file = "test.csv"
    df = pd.DataFrame({"id": [1, 2], "title": ["Doc 1", "Doc 2"], "content": ["Content A", "Content B"]})
    df.to_csv(csv_file, index=False)
    
    csv_input = {
        "source_type": "csv",
        "content": os.path.abspath(csv_file)
    }
    csv_res = await extract_content(csv_input)
    print(f"\nCSV Extraction Status: {csv_res['status']}")
    print(f"Content Preview: {csv_res['extracted_content'][:2]}")
    
    # Clean up test file
    if os.path.exists(csv_file):
        os.remove(csv_file)

    # 3. PDF Test (Mock or Real if possible)
    # Since I don't have a real legal PDF handy, I'll just check if it fails gracefully
    pdf_input = {
        "source_type": "pdf",
        "content": "non_existent.pdf"
    }
    pdf_res = await extract_content(pdf_input)
    print(f"\nPDF (missing) Status: {pdf_res['status']}")
    print(f"Error: {pdf_res.get('error')}")

if __name__ == "__main__":
    asyncio.run(test_extractor())

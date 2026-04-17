import asyncio
import os
from app.pipeline.orchestrator import SourceOrchestrator
from app.core.logger import logger

async def test_handlers():
    orchestrator = SourceOrchestrator()
    
    # 1. Test Local File (Text)
    test_file = "scratch/temp_test_file.txt"
    os.makedirs("scratch", exist_ok=True)
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("This is a local text file content for testing.")
    
    logger.info("--- Testing Local File (Text) ---")
    res_local = await orchestrator.route_and_fetch(test_file)
    print(f"Local Text Result: {res_local['strategy']} | Content: {res_local['content']}")
    
    # 2. Test Local File (PDF Routing)
    dummy_pdf = "scratch/dummy_law_act.pdf"
    with open(dummy_pdf, "wb") as f:
        f.write(b"%PDF-1.4\n%mock content")
    
    logger.info("--- Testing Local File (PDF Routing) ---")
    try:
        res_pdf = await orchestrator.route_and_fetch(dummy_pdf)
        print(f"Local PDF Result Strategy: {res_pdf['strategy']} | Content: {res_pdf['content']}")
    except Exception as e:
        print(f"Local PDF Failed: {e}")

    # 3. Test HuggingFace (Routing and small fetch)
    logger.info("--- Testing HuggingFace ---")
    try:
        # Using a known small dataset
        res_hf = await orchestrator.route_and_fetch("hf:imdb")
        print(f"HF Result Strategy: {res_hf['strategy']}")
        print(f"HF Content Sample: {str(res_hf['content'])[:200]}...")
    except Exception as e:
        print(f"HF Failed: {e}")

    # Clean up
    for f in [test_file, dummy_pdf]:
        if os.path.exists(f):
            os.remove(f)

if __name__ == "__main__":
    asyncio.run(test_handlers())

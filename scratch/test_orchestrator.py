import asyncio
import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.pipeline.orchestrator import SourceOrchestrator

async def test_orchestrator():
    orchestrator = SourceOrchestrator()
    
    print("--- Test 1: URL ---")
    # Using a fake URL but it will trigger the branch
    # result = await orchestrator.route_and_fetch("https://google.com")
    # print(f"Strategy: {result['strategy']}")
    
    print("--- Test 2: HF Dataset ---")
    result = await orchestrator.route_and_fetch("HF:169Pi/indian_law")
    print(f"Strategy: {result['strategy']}")
    
    print("--- Test 3: Local File ---")
    result = await orchestrator.route_and_fetch("docs/test.pdf")
    print(f"Strategy: {result['strategy']}")

if __name__ == "__main__":
    asyncio.run(test_orchestrator())

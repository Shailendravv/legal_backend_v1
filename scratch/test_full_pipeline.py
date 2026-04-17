import asyncio
import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.api.v1.endpoints.chat import chat_interaction, ChatRequest

async def test_chat_pipeline():
    print("--- Testing Unified Pipeline with HF (Mocked) ---")
    request = ChatRequest(user_query="HF:169Pi/indian_law")
    response = await chat_interaction(request)
    print(f"Orchestrator Strategy: {response['pipeline_metadata']['orchestrator_strategy']}")
    print(f"Status: {response['pipeline_metadata']['status']}")
    print(f"Output Preview: {response['output']['preview']}")
    
    print("\n--- Testing Unified Pipeline with Search (Dynamic) ---")
    # This will actually hit the crawler if not careful, but I'll use a term that might be cached or just let it run
    request = ChatRequest(user_query="IPC 302")
    response = await chat_interaction(request)
    print(f"Resolved Act: {response['legal_context']['resolved_act']}")
    print(f"Strategy: {response['pipeline_metadata']['orchestrator_strategy']}")
    print(f"PII Detected: {response['processing_stages']['cleaning']['pii_detected']}")

if __name__ == "__main__":
    asyncio.run(test_chat_pipeline())

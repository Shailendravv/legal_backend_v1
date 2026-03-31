from typing import List, Dict
from app.core.logger import logger

def build_system_prompt() -> str:
    """
    Constructs the core persona and instructions for the Indian Legal AI.
    """
    return (
        "You are 'LegalAI India', an advanced legal assistant specializing in Indian Law. "
        "Your goal is to provide accurate, concise, and helpful legal information based on the context provided. "
        "Strictly adhere to the following rules:\n"
        "1. Only answer based on the provided legal context if possible.\n"
        "2. Cite sections and acts clearly, e.g., [Section 302, IPC].\n"
        "3. If the answer is not in the context, state that you do not know but can provide general legal principles.\n"
        "4. Always include a disclaimer that this is for informational purposes and not a substitute for professional legal advice.\n"
        "5. Maintain a professional and objective tone."
    )

def build_context(chunks: List[Dict]) -> str:
    """
    Aggregates retrieved legal document chunks into a single context string.
    """
    context_str = ""
    for i, chunk in enumerate(chunks, 1):
        context_str += f"Source {i}:\n{chunk['content']}\n"
    return context_str.strip()

def build_messages(system_prompt: str, context: str, history: List[Dict], user_query: str) -> List[Dict]:
    """
    Assembles the final list of messages for the LLM chat completion API.
    """
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add conversation history
    for turn in history:
        messages.append({"role": turn['role'], "content": turn['content']})

    # Add current query with context
    current_content = f"Context from Legal Sources:\n{context}\n\nUser Question: {user_query}"
    messages.append({"role": "user", "content": current_content})
    
    return messages

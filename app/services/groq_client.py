from groq import AsyncGroq
from app.core.config import settings
from app.core.logger import logger
from typing import List, Dict, AsyncGenerator

class GroqClient:
    def __init__(self):
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)

    async def stream_completion(self, messages: List[Dict], model: str = "llama-3.3-70b-versatile") -> AsyncGenerator[str, None]:
        """
        Calls Groq API with streaming enabled and yields tokens as they arrive.
        """
        try:
            stream = await self.client.chat.completions.create(
                messages=messages,
                model=model,
                stream=True,
                temperature=0.1,  # Low temperature for factual consistency
                max_tokens=1024
            )
            async for chunk in stream:
                token = chunk.choices[0].delta.content
                if token:
                    yield token
        except Exception as e:
            logger.error(f"Error during Groq streaming: {str(e)}")
            yield f"Error: {str(e)}"

groq_client = GroqClient()


from groq import Groq
from app.core.config import settings

class GroqClient:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    def generate_response(self, prompt: str, model: str = "llama-3.3-70b-versatile"):
        completion = self.client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model=model,
        )
        return completion.choices[0].message.content

groq_client = GroqClient()

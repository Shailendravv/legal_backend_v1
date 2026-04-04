import httpx
from typing import Optional

class CrawlerClient:
    def __init__(self, timeout: int = 30):
        self._client = httpx.AsyncClient(timeout=timeout)

    async def get(self, url: str) -> Optional[str]:
        response = await self._client.get(url)
        if response.status_code == 200:
            return response.text
        return None

    async def close(self):
        await self._client.aclose()

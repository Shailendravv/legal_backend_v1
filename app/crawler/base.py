from abc import ABC, abstractmethod
from typing import Any, List

class BaseCrawler(ABC):
    @abstractmethod
    async def crawl(self, url: str) -> str:
        """Fetch raw content from a URL."""
        pass
    
    @abstractmethod
    def parse(self, raw_html: str) -> Any:
        """Transform raw HTML into structured data."""
        pass

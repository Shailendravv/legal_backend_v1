from typing import Dict, Type
from app.crawler.base import BaseCrawler

class CrawlerRegistry:
    def __init__(self):
        self._crawlers: Dict[str, Type[BaseCrawler]] = {}

    def register(self, name: str, crawler_cls: Type[BaseCrawler]):
        self._crawlers[name] = crawler_cls

    def get(self, name: str) -> Type[BaseCrawler]:
        return self._crawlers.get(name)

crawler_registry = CrawlerRegistry()

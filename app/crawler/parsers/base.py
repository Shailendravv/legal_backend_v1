from abc import ABC, abstractmethod
from typing import Any

class BaseParser(ABC):
    @abstractmethod
    def parse(self, content: str) -> Any:
        """Process content into structured output."""
        pass

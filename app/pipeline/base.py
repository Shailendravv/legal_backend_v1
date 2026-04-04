from abc import ABC, abstractmethod
from typing import Any, List

class Stage(ABC):
    @abstractmethod
    async def run(self, input_data: Any) -> Any:
        """Execute logic for this pipeline stage."""
        pass

class Pipeline:
    def __init__(self, name: str, stages: List[Stage]):
        self.name = name
        self.stages = stages

    async def execute(self, initial_data: Any) -> Any:
        current_data = initial_data
        for stage in self.stages:
            current_data = await stage.run(current_data)
        return current_data

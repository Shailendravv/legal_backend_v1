from typing import Any
from app.pipeline.base import Pipeline

class PipelineExecutor:
    async def run(self, pipeline: Pipeline, data: Any) -> Any:
        # Placeholder for more complex execution logic (e.g. error handling, retries)
        return await pipeline.execute(data)

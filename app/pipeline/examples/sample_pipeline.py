from app.pipeline.base import Stage, Pipeline
from typing import Any

class ExampleStage(Stage):
    def __init__(self, increment: int):
        self.increment = increment

    async def run(self, input_data: int) -> int:
        return input_data + self.increment

sample_pipeline = Pipeline(
    name="Sample Calc Pipeline",
    stages=[ExampleStage(10), ExampleStage(5)]
)

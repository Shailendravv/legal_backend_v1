from typing import Any, List

class CrawlerStage:
    def __init__(self, name: str):
        self.name = name

    async def execute(self, content: Any) -> Any:
        # Placeholder for stage processing
        return content

class CleanStage(CrawlerStage):
    def __init__(self):
        super().__init__("Clean")

class FormatStage(CrawlerStage):
    def __init__(self):
        super().__init__("Format")

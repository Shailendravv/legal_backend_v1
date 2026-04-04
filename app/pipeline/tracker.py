from typing import Dict, Any

class PipelineTracker:
    def __init__(self):
        self._progress: Dict[str, float] = {}

    def update_progress(self, pipeline_id: str, progress: float):
        self._progress[pipeline_id] = progress

    def get_progress(self, pipeline_id: str) -> float:
        return self._progress.get(pipeline_id, 0.0)

tracker = PipelineTracker()

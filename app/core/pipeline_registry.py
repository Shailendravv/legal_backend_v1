from typing import Dict, Any

class PipelineRegistry:
    def __init__(self):
        self._execution_history: Dict[str, Any] = {}

    def track_execution(self, pipeline_id: str, state: Any):
        self._execution_history[pipeline_id] = state

    def get_execution_state(self, pipeline_id: str) -> Any:
        return self._execution_history.get(pipeline_id)

registry = PipelineRegistry()

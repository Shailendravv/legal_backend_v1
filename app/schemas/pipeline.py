from pydantic import BaseModel
from typing import List, Optional

class PipelineRequest(BaseModel):
    pipeline_type: str
    input_params: dict

class PipelineResponse(BaseModel):
    pipeline_id: str
    status: str
    message: Optional[str] = None

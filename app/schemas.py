from pydantic import BaseModel, Field
from typing import Optional

class TransformRequest(BaseModel):
    transform_map_id: int = 1

class AIRequest(BaseModel):
    import_set_id: Optional[int] = None
    question: str = Field(default="Explain the latest import results and identify data-quality concerns.", max_length=2000)

from pydantic import BaseModel
from typing import Optional


class CreateAIExplanationResponse(BaseModel):
    code: int
    message: str
    data: Optional[dict]

from pydantic import BaseModel
from typing import List, Optional

class TestModeQuestionDTO(BaseModel):
    answer_rate: float
    section: str
    description: str
    description_detail: Optional[str]
    description_image: Optional[str]
    options: List[str]

class TestModeResponse(BaseModel):
    code: int
    message: str
    data: Optional[dict]

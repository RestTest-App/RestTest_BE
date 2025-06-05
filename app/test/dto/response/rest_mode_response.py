from pydantic import BaseModel
from typing import List, Optional

class RestModeQuestionDTO(BaseModel):
    question_id: int
    answer_rate: float
    section: str
    description: str
    description_detail: Optional[str]
    description_image: Optional[str]
    options: List[str]
    answer: int
    option_explanations: List[str]

class RestModeResponse(BaseModel):
    code: int
    message: str
    data: Optional[dict]

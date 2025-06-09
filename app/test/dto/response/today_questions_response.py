from pydantic import BaseModel
from typing import Optional, List

class TodayQuestionDTO(BaseModel):
    description: str
    description_detail: Optional[str]
    options: List[str]
    answer: int
    option_explanations: List[str]

class TodayQuestionsResponse(BaseModel):
    code: int
    message: str
    data: Optional[dict]

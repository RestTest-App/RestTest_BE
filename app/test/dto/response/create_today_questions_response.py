from pydantic import BaseModel
from typing import List, Optional

class QuestionDTO(BaseModel):
    question_id: str
    description: str
    description_detail: str
    options: List[str]
    answer: int
    option_explanations: List[str]

class CreateTodayQuestionsResponse(BaseModel):
    code: int
    message: str
    data: Optional[dict] = None
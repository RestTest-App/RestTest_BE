# app/studybook/studybook_question/dto/request/add_question_request_dto.py
from pydantic import BaseModel, Field
from typing import List, Optional

class AddQuestionRequestDTO(BaseModel):
    studybook_id: int
    description: str
    options: List[str] = Field(min_items=2)
    answer: int
    explanation: Optional[str] = None
    option_explanations: Optional[List[str]] = None

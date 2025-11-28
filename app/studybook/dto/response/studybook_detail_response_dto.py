# app/studybook/dto/response/studybook_detail_response_dto.py
from pydantic import BaseModel
from typing import List, Optional

class QuestionItemDTO(BaseModel):
    id: int
    description: str
    options: List[str]
    answer: int
    explanation: Optional[str] = None

class StudybookDetailDTO(BaseModel):
    id: int
    name: str
    question_count: int
    file_color: str
    questions: List[QuestionItemDTO]

class StudybookDetailResponseDTO(BaseModel):
    code: int
    message: str
    data: StudybookDetailDTO

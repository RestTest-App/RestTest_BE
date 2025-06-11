# app/studybook/studybook_question/dto/response/add_question_response_dto.py
from pydantic import BaseModel

class AddQuestionResponseDTO(BaseModel):
    question_id: int
    message: str

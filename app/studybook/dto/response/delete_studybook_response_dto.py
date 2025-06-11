# app/studybook/dto/response/delete_studybook_response_dto.py
from pydantic import BaseModel

class DeleteStudybookResponseDTO(BaseModel):
    message: str

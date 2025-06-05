# app/studybook/dto/response/upload_studybook_response_dto.py

from pydantic import BaseModel

class UploadStudybookResponseDTO(BaseModel):
    studybook_id: int
    message: str

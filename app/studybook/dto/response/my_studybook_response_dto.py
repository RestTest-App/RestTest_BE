from pydantic import BaseModel
from datetime import datetime
from typing import List

class StudyBookItemDTO(BaseModel):
    id: int
    name: str
    question_count: int
    file_color: str
    created_at: datetime

class MyStudybookResponseDTO(BaseModel):
    studybooks: List[StudyBookItemDTO]

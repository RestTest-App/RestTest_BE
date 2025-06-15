from pydantic import BaseModel, Field
from typing import List

class DummyQuestionDTO(BaseModel):
    description: str
    options: List[str] = Field(..., min_items=4, max_items=4)
    answer: int  # 1~4

class UploadDummyStudybookRequestDTO(BaseModel):
    studybook_name: str
    questions: List[DummyQuestionDTO]

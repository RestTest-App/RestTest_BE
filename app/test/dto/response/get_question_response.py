from pydantic import BaseModel, Field
from typing import List, Optional

class GetQuestionResponse(BaseModel):
    question_id: int = Field(..., description="문제 ID")
    section: str = Field(..., description="문제 영역")
    description: str = Field(..., description="문제 설명")
    options: List[str] = Field(..., description="문제 보기")
    answer: int = Field(..., description="정답 index")
    exam_section_id: int = Field(..., description="과목 ID")

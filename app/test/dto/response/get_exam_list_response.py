from pydantic import BaseModel, Field
from typing import List, Optional

class ExamItemResponse(BaseModel):
    exam_id: int = Field(..., description="시험 ID")
    exam_name: str = Field(..., description="시험 이름")
    question_count: int = Field(..., description="문제 수")
    exam_time: int = Field(..., description="시험 시간")
    pass_rate: Optional[float] = Field(None, description="합격률")

class PaginationResponse(BaseModel):
    offset: int
    limit: int
    total_count: int
    next_page: bool

class GetExamListResponse(BaseModel):
    goal: Optional[int] = None
    archive: Optional[int] = None
    certificates: List[int]
    selected_certificate_name: str
    exams: List[ExamItemResponse]
    pagenation: PaginationResponse

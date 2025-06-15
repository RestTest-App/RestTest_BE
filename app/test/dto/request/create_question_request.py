from pydantic import BaseModel, Field
from typing import List, Optional

class CreateQuestionRequest(BaseModel):
    section: str = Field(..., description="문제 영역 (section)")
    description: str = Field(..., description="문제 설명")
    description_detail: Optional[str] = Field(None, description="문제 상세 설명 (optional)")
    description_image: Optional[str] = Field(None, description="문제 참고 이미지 (optional)")
    options: List[str] = Field(..., description="문제 보기 (LIST[STRING])")
    answer: int = Field(..., description="정답 (보기 index)")
    option_explanations: Optional[List[str]] = Field(None, description="보기 별 해설 (optional)")
    exam_section_id: int = Field(..., description="과목 ID (ExamSection)")

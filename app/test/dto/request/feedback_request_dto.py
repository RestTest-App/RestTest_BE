from pydantic import BaseModel, Field
from typing import List

class FeedbackRequestDTO(BaseModel):
    test_id: str = Field(..., description="시험 ID")
    question_id: str = Field(..., description="문제 ID")
    ai_explanation: List[str] = Field(..., description="AI가 생성한 해설 목록")
    feedback: str = Field(..., description="사용자 피드백 내용")

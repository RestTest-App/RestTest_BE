from pydantic import BaseModel, Field

class GetExamInfoResponse(BaseModel):
    year: int = Field(..., description="시험 년도")
    month: int = Field(..., description="시험 월")
    name: str = Field(..., description="시험 이름")
    question_count: int = Field(..., description="문제 수")
    time: int = Field(..., description="시험 시간 (분)")
    exam_attempt: int = Field(..., description="시험 응시 회차")
    pass_rate: float = Field(..., description="합격률 (%)")

from pydantic import BaseModel, Field
from typing import Optional

class CreateExamRequest(BaseModel):
    name: str = Field(..., description="시험 이름")
    pass_rate: float = Field(..., description="시험 합격률")
    year: int = Field(..., description="시험 응시 년도")
    month: int = Field(..., description="시험 응시 월")
    trial: Optional[int] = Field(None, description="시험 회차 (선택)")
    time: int = Field(..., description="시험 진행 시간 (분 단위)")
    certificate_id: int = Field(..., description="자격증 ID")

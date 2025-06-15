from pydantic import BaseModel, Field
from typing import List

class CreateDummyDataRequest(BaseModel):
    certificate_name: str = Field(..., description="자격증 이름")
    exam_names: List[str] = Field(..., description="시험 이름 리스트")
    section_names: List[str] = Field(..., description="과목(Section) 이름 리스트")
    questions_per_section: int = Field(..., description="Section 당 생성할 문제 수")
    exam_time: int = Field(..., description="시험 시간 (분)")
    pass_rate: float = Field(..., description="합격률 (%)")

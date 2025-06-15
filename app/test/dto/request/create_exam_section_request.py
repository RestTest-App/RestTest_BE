from pydantic import BaseModel, Field

class CreateExamSectionRequest(BaseModel):
    name: str = Field(..., description="과목 이름")
    order: int = Field(..., description="과목 순서")
    exam_id: int = Field(..., description="시험 ID")

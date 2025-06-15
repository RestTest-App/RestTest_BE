from pydantic import BaseModel, Field

class GetExamSectionResponse(BaseModel):
    exam_section_id: int = Field(..., description="과목 ID")
    name: str = Field(..., description="과목 이름")
    order: int = Field(..., description="과목 순서")

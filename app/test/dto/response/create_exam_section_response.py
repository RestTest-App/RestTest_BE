from pydantic import BaseModel, Field

class CreateExamSectionResponse(BaseModel):
    exam_section_id: int = Field(..., description="생성된 과목 ID")

from pydantic import BaseModel, Field

class CreateExamResponse(BaseModel):
    exam_id: int = Field(..., description="생성된 시험 ID")

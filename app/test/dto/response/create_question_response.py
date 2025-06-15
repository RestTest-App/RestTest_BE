from pydantic import BaseModel, Field

class CreateQuestionResponse(BaseModel):
    question_id: int = Field(..., description="생성된 문제 ID")

from datetime import datetime  # 변경!
from pydantic import BaseModel, ConfigDict

class QuestionInfo(BaseModel):
    question_id: int
    answer_rate: float
    section: str
    description: str
    description_detail: str
    description_image: str
    options: list[str]
    option_explanations: list[str]
    answer: int
    selected_answer : int
    is_correct : bool

    model_config = ConfigDict(from_attributes=True)

class GetReviewRestModeResponse(BaseModel):
    review_note_id: int
    name: str
    created_at: datetime
    updated_at: datetime
    certificate_name: str
    question_count: int
    questions: list[QuestionInfo]

    model_config = ConfigDict(from_attributes=True)

from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ExamInfo(BaseModel):
    exam_id: int
    name: str
    year: int
    month: int
    trial: int
    time: int
    pass_rate: float
    score: int
    is_passed: bool
    solved_at: datetime

    model_config = ConfigDict(from_attributes=True)

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


class GetReviewTestModeResponse(BaseModel):
    review_note_id: int
    created_at: datetime
    exam: ExamInfo
    questions: list[QuestionInfo]

    model_config = ConfigDict(from_attributes=True)

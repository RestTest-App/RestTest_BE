from typing import Optional, List

from pydantic import BaseModel


class QuestionInfo(BaseModel):
    question_id: int
    answer_rate: float
    section: str
    description: str
    description_detail: Optional[str]
    description_image: Optional[str]
    options: List[str]
    option_explanations: List[str]
    answer: int
    selected_answer: Optional[int]
    is_correct: bool
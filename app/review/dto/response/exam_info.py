from datetime import datetime

from pydantic.v1 import BaseModel


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
from pydantic import BaseModel


class ExamItemInfo(BaseModel):
    review_note_id: int
    exam_id: int
    name: str
    is_passed: bool
    certificate: str
    read_count: int
    pass_rate: float
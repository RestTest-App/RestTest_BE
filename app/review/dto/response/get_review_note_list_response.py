from xmlrpc.client import DateTime
from pydantic import BaseModel, ConfigDict

class ExamListInfo(BaseModel):
    review_note_id: int
    name: str
    exam_id: str
    certificate: str
    read_count: int
    pass_rate: float
    is_passed: bool

    model_config = ConfigDict(from_attributes=True)

class GetReviewNoteListResponse(BaseModel):
    category: list[str]
    selected_category: str
    exams:list[ExamListInfo]

    model_config = ConfigDict(from_attributes=True)

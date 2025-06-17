from datetime import datetime
from typing import List

from pydantic import BaseModel

from app.review.dto.response.exam_info import ExamInfo
from app.review.dto.response.question_info import QuestionInfo


class ReviewNoteDetailResponseDto(BaseModel):
    review_note_id: int
    created_at: datetime
    exam: ExamInfo
    questions: List[QuestionInfo]
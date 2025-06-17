from typing import List

from pydantic import BaseModel

from app.review.dto.response.exam_item_info import ExamItemInfo


class ReviewNoteListResponseDto(BaseModel):
    category: str
    selected_category: str
    exams: List[ExamItemInfo]
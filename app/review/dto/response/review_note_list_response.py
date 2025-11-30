from typing import List, Optional

from pydantic import BaseModel

from app.review.dto.response.exam_item_info import ExamItemInfo


class ReviewNoteListResponseDto(BaseModel):
    category: List[str]
    selected_category: Optional[str] = None
    exams: List[ExamItemInfo]
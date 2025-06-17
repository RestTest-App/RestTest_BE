from typing import List
from pydantic import BaseModel

from app.review.dto.request.question_info import QuestionInfoResponseDto


class AddReviewNoteTestRequestDto(BaseModel):
    result_id: int
    test_id: int
    question_list: List[QuestionInfoResponseDto]
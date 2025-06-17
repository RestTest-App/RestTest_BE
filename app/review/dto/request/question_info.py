from pydantic import BaseModel


class QuestionInfoResponseDto(BaseModel):
    test_tracker_id: int
    question_id: int
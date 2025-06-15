from pydantic import BaseModel
from typing import Optional

from app.test.dto.response.answer_info import AnswerInfoDto
from app.test.dto.response.test_log import TestLogDto


class SubmitTestResponseDTO(BaseModel):
    test_log: TestLogDto
    correct_answer: list[int]
    correct_answer_info: Optional[AnswerInfoDto]
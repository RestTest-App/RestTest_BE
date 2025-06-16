from typing import Optional

from pydantic import BaseModel

# 시험 결과 문항별 제출 답안 dto (null 허용)
class SubmitTestRequestDTO(BaseModel):
    answers: list[Optional[int]]
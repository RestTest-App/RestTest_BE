from typing import Dict

from pydantic import BaseModel


class AnswerInfoDto(BaseModel):
    answer: int
    option_explanation: Dict[str, str]
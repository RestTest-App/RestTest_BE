from pydantic import BaseModel


class AnswerInfoDto(BaseModel):
    answer: int
    option_explanation: dict[str, str]
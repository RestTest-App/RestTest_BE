from pydantic import BaseModel

class ExamResponseDTO(BaseModel):
    id: int
    name: str
    year: int
    month: int
    trial: int | None
    time: int
    pass_rate: float | None
    question_count: int

    class Config:
        from_attributes = True
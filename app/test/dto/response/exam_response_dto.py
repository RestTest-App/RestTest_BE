from pydantic import BaseModel

class ExamResponseDTO(BaseModel):
    id: int
    name: str
    year: int
    month: int
    trial: int | None
    time: int
    pass_rate: float | None

    class Config:
        from_attributes = True  # ✅ Pydantic v2 대응
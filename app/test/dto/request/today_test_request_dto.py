from pydantic import BaseModel

class TodayTestRequestDTO(BaseModel):
    certificate_id: int
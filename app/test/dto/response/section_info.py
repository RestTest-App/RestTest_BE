from pydantic import BaseModel


class SectionInfoDto(BaseModel):
    section_name: str
    correct_count: int
    total_count: int
    score: int
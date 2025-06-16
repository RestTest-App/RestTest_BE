from openai import BaseModel


class PaginationDto(BaseModel):
    offset: int
    limit: int
    total_count: int
    next_page: bool
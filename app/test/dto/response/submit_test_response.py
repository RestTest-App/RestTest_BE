from pydantic import BaseModel
from typing import Optional


class SubmitTestResponse(BaseModel):
    code: int
    message: str
    data: Optional[dict] = None

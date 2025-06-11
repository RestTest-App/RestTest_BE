from pydantic import BaseModel
from typing import List, Optional


class SubmitTestRequest(BaseModel):
    answers: List[Optional[int]]

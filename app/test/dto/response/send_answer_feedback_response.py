from pydantic import BaseModel
from typing import Optional

class SendAnswerFeedbackResponse(BaseModel):
    code: int
    message: str
    data: Optional[dict] = None
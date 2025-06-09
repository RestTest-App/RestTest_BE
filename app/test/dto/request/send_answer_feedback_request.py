from pydantic import BaseModel

class SendAnswerFeedbackRequest(BaseModel):
    test_id: str
    question_id: str
    ai_explanation: str
    feedback: str
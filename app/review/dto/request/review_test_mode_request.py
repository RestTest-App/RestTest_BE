from pydantic import BaseModel

class ReviewTestModeRequest(BaseModel):
    test_id: str
    result_id: str
    question_id: str
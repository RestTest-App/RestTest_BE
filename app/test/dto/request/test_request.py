from pydantic import BaseModel

class TestRequest(BaseModel):
    name: str
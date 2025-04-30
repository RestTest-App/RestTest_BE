# 클라이언트에게 보내는 데이터 형식 정의 (스키마)
from pydantic import BaseModel, ConfigDict


class TestResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

from pydantic import BaseModel


class SignUpRequest(BaseModel):
    auth_provider: str
    email: str
    nickname: str
    gender: str
    birthday: str
    job: str
    certificates: list[int] # 자격증 리스트
    agree_to_terms: bool
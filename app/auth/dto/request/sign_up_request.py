from pydantic import BaseModel


class SignUpRequest(BaseModel):
    code : str # 카카오 인가 코드
    nickname: str
    gender: str
    birthday: str
    job: str
    certificates: list[int] # 자격증 리스트
    agree_to_terms: bool
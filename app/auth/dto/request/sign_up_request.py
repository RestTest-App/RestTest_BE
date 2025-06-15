from pydantic import BaseModel


class SignUpRequest(BaseModel):
    kakao_token : str # 카카오 인가 코드
    email : str
    nickname: str
    gender: str
    birthday: str
    job: str
    certificates: list[int] # 자격증 리스트
    agree_to_terms: bool
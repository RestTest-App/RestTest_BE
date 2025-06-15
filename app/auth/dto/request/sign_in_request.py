from pydantic import BaseModel


class SignInRequest(BaseModel):
    kakao_token: str
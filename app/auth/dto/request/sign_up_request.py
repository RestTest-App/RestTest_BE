from pydantic import BaseModel, Field


class SignUpRequest(BaseModel):
    kakao_token: str = Field(..., description="카카오 인가 코드")
    email: str = Field(..., description="이메일")
    nickname: str = Field(..., description="닉네임 (2-20자)")
    gender: str = Field(default="M", description="성별 (M/F/male/female/남성/여성)")
    birthday: str = Field(default="2000-01-01", description="생년월일 (YYYY-MM-DD)")
    job: str = Field(default="", description="직업")
    certificates: list[int] = Field(default_factory=list, description="자격증 ID 리스트")
    agree_to_terms: bool = Field(default=True, description="약관 동의")
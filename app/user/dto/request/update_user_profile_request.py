from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


class UpdateUserProfileRequest(BaseModel):
    """프로필(닉네임, 이미지) 수정 요청 DTO"""

    nickname: Optional[str] = Field(None, min_length=2, max_length=20, description="닉네임 (2-20자)")
    delete_image: bool = Field(False, description="true 시 프로필 이미지 삭제")

    @field_validator('nickname')
    @classmethod
    def validate_nickname(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v

        # 한글, 영문, 숫자, 일부 특수문자(_-.)만 허용
        if not re.match(r'^[가-힣a-zA-Z0-9._-]+$', v):
            raise ValueError('올바른 닉네임 형식이 아닙니다.')

        return v
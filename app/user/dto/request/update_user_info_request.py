from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class UpdateUserInfoRequest(BaseModel):
    """사용자 정보(모든 필드) 수정 요청 DTO - JSON 형식"""

    nickname: Optional[str] = Field(None, min_length=2, max_length=20, description="닉네임 (2-20자)")
    gender: Optional[str] = Field(None, description="성별")
    birthday: Optional[str] = Field(None, description="생년월일 (YYYY-MM-DD)")
    job: Optional[str] = Field(None, max_length=100, description="직업")
    rest_goal: Optional[int] = Field(None, ge=0, description="쉬엄모드 목표")
    test_goal: Optional[int] = Field(None, ge=0, description="시험모드 목표")
    goal_table: Optional[list[int]] = Field(None, description="목표 테이블 (목표 번호 리스트)")

    @field_validator('nickname')
    @classmethod
    def validate_nickname(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v

        # 한글, 영문, 숫자, 일부 특수문자(_-.)만 허용
        if not re.match(r'^[가-힣a-zA-Z0-9._-]+$', v):
            raise ValueError('올바른 닉네임 형식이 아닙니다.')

        return v

    @field_validator('birthday')
    @classmethod
    def validate_birthday(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v

        # YYYY-MM-DD 형식 검증
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError('생년월일은 YYYY-MM-DD 형식이어야 합니다.')

        return v

    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v

        if v not in ['M', 'F', 'male', 'female', '남성', '여성']:
            raise ValueError('올바른 성별 형식이 아닙니다.')

        return v

    @field_validator('goal_table')
    @classmethod
    def validate_goal_table(cls, v: Optional[list[int]]) -> Optional[list[int]]:
        if v is None:
            return v

        # goal_table은 1-7 범위의 정수 리스트
        if not isinstance(v, list):
            raise ValueError('goal_table은 리스트 형식이어야 합니다.')

        for goal_id in v:
            if not isinstance(goal_id, int) or goal_id < 1 or goal_id > 7:
                raise ValueError('goal_table의 값은 1-7 범위의 정수여야 합니다.')

        return v
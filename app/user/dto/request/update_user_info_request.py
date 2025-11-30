from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict
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
    goal_table: Optional[Dict[str, Optional[int]]] = Field(None, description="목표 테이블 {daily_problem, daily_accuracy, consecutive_days}")

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
    def validate_goal_table(cls, v: Optional[Dict[str, Optional[int]]]) -> Optional[Dict[str, Optional[int]]]:
        if v is None:
            return v

        # goal_table은 dict 형식
        if not isinstance(v, dict):
            raise ValueError('goal_table은 dict 형식이어야 합니다.')

        # 허용되는 카테고리
        allowed_categories = {'daily_problem', 'daily_accuracy', 'consecutive_days'}

        for category, value in v.items():
            if category not in allowed_categories:
                raise ValueError(f'목표 카테고리는 {allowed_categories} 중 하나여야 합니다.')

            # 값이 None이거나 0 이상의 정수여야 함
            if value is not None:
                if not isinstance(value, int) or value <= 0:
                    raise ValueError(f'{category}의 값은 양의 정수이거나 null이어야 합니다.')

        return v
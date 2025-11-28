from pydantic import BaseModel
from typing import Optional


class UpdateUserInfoResponse(BaseModel):
    """사용자 정보 수정 응답 DTO"""

    id: int
    nickname: str
    gender: str
    birthday: str
    job: str
    rest_goal: Optional[int] = None
    test_goal: Optional[int] = None
    goal_table: Optional[list[int]] = None  # 목표 ID 리스트
    profile_image: Optional[str] = None
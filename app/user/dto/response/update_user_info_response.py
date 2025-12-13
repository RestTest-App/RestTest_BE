from pydantic import BaseModel
from typing import Optional, Dict


class UpdateUserInfoResponse(BaseModel):
    """사용자 정보 수정 응답 DTO"""

    id: int
    nickname: str
    gender: str
    birthday: str
    job: str
    rest_goal: Optional[int] = None
    test_goal: Optional[int] = None
    goal_table: Optional[Dict[str, Optional[int]]] = None  # 목표 {daily_problem, daily_accuracy, consecutive_days}
    profile_image: Optional[str] = None
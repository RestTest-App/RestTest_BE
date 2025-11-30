"""
목표 진행도 관련 Response DTO
"""
from typing import List
from pydantic import BaseModel


class GoalProgressDto(BaseModel):
    """개별 목표의 진행도"""
    goal_id: int
    goal_name: str
    goal_type: str
    target_value: int
    current_progress: float
    progress_percent: float
    is_achieved: bool


class AllGoalsProgressResponse(BaseModel):
    """모든 목표의 진행도"""
    today_date: str
    total_goals: int
    achieved_goals: int
    overall_progress: float
    goals: List[GoalProgressDto]

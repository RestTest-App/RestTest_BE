# core/auth.py

from fastapi import Depends
from domain.user.entity.user import User


def get_current_user() -> User:
    # 임시 mock 유저 객체
    return User(
        id=1,
        auth_provider="mock",
        email="mock@example.com",
        nickname="테스트유저",
        gender="none",
        birthday=None,
        job="학생",
        agree_to_terms=True,
        created_at=None,
        studybook_limit=5,
        rest_goal=None,
        test_goal=None,
        profile_image=None,
        total_study_days=0,
        is_study_today=False
    )

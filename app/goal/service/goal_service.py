"""
사용자 목표 진행도 관련 비즈니스 로직
"""
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, func
from sqlalchemy.future import select

from app.goal.constants.goal_config import GOAL_CONFIGS
from domain.test.entity.test_tracker import TestTracker
from domain.test.entity.user_question_tracker import UserQuestionTracker
from domain.user.entity.user import User


class GoalService:
    """목표 진행도 조회 서비스"""

    @staticmethod
    async def get_goal_progress(
        db: AsyncSession,
        user_id: int,
        goal_id: int
    ) -> dict:
        """
        사용자의 특정 목표에 대한 오늘의 진행 상황을 조회합니다.

        Args:
            db: AsyncSession
            user_id: 사용자 ID
            goal_id: 목표 ID

        Returns:
            {
                "goal_id": int,
                "goal_name": str,
                "goal_type": str,
                "target_value": int,
                "current_progress": int or float,
                "progress_percent": float,
                "is_achieved": bool
            }
        """
        # 1. 목표 설정 조회
        goal_config = GOAL_CONFIGS.get(goal_id)
        if not goal_config:
            return {
                "goal_id": goal_id,
                "error": "존재하지 않는 목표입니다"
            }

        goal_type = goal_config["goal_type"]
        target_value = goal_config["target_value"]
        today = datetime.now().date()

        # 2. 목표 타입별 진행도 계산
        if goal_type == "daily_problem":
            current_progress = await GoalService._get_daily_problem_count(
                db, user_id, today
            )
            progress_percent = min((current_progress / target_value) * 100, 100)
            is_achieved = current_progress >= target_value

        elif goal_type == "daily_accuracy":
            current_progress, progress_percent = await GoalService._get_daily_accuracy(
                db, user_id, today
            )
            is_achieved = current_progress >= target_value

        elif goal_type == "consecutive_study_days":
            current_progress = await GoalService._get_consecutive_study_days(
                db, user_id
            )
            progress_percent = min((current_progress / target_value) * 100, 100)
            is_achieved = current_progress >= target_value

        else:
            return {
                "goal_id": goal_id,
                "error": "지원하지 않는 목표 타입입니다"
            }

        # 3. 결과 반환
        return {
            "goal_id": goal_id,
            "goal_name": goal_config["name"],
            "goal_type": goal_type,
            "target_value": target_value,
            "current_progress": current_progress,
            "progress_percent": round(progress_percent, 1),
            "is_achieved": is_achieved
        }

    @staticmethod
    async def get_all_goals_progress(
        db: AsyncSession,
        user_id: int
    ) -> dict:
        """
        사용자의 모든 목표(goal_table)에 대한 진행 상황을 조회합니다.

        Args:
            db: AsyncSession
            user_id: 사용자 ID

        Returns:
            {
                "today_date": str,
                "total_goals": int,
                "achieved_goals": int,
                "overall_progress": float,
                "goals": list[dict]
            }
        """
        # 1. 사용자의 goal_table 조회
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return {
                "error": "사용자를 찾을 수 없습니다"
            }

        goal_table = user.goal_table
        if not goal_table:
            return {
                "today_date": datetime.now().date().isoformat(),
                "total_goals": 0,
                "achieved_goals": 0,
                "overall_progress": 0,
                "goals": []
            }

        # 2. 각 목표별 진행도 계산 (goal_table은 dict 형식)
        goals_progress = []
        for category, target_value in goal_table.items():
            # null 또는 None 값은 건너뜀
            if target_value is None:
                continue

            goal_progress = await GoalService._get_goal_progress_by_category(
                db, user_id, category, target_value
            )
            goals_progress.append(goal_progress)

        # 3. 전체 진행도 통계
        achieved_count = sum(1 for goal in goals_progress if goal.get("is_achieved", False))
        total_count = len(goals_progress)
        overall_progress = (achieved_count / total_count * 100) if total_count > 0 else 0

        return {
            "today_date": datetime.now().date().isoformat(),
            "total_goals": total_count,
            "achieved_goals": achieved_count,
            "overall_progress": round(overall_progress, 1),
            "goals": goals_progress
        }

    @staticmethod
    async def _get_goal_progress_by_category(
        db: AsyncSession,
        user_id: int,
        category: str,
        target_value: int
    ) -> dict:
        """
        카테고리와 목표값을 기반으로 진행도를 계산합니다.

        Args:
            db: AsyncSession
            user_id: 사용자 ID
            category: 목표 카테고리 (daily_problem, daily_accuracy, consecutive_days)
            target_value: 목표값

        Returns:
            {
                "category": str,
                "goal_name": str,
                "target_value": int,
                "current_progress": int or float,
                "progress_percent": float,
                "is_achieved": bool
            }
        """
        today = datetime.now().date()

        if category == "daily_problem":
            current_progress = await GoalService._get_daily_problem_count(
                db, user_id, today
            )
            progress_percent = min((current_progress / target_value) * 100, 100)
            is_achieved = current_progress >= target_value
            goal_name = f"하루에 {target_value}문제"

        elif category == "daily_accuracy":
            current_progress, _ = await GoalService._get_daily_accuracy(
                db, user_id, today
            )
            progress_percent = min((current_progress / target_value) * 100, 100) if current_progress > 0 else 0
            is_achieved = current_progress >= target_value
            goal_name = f"정답률 {target_value}% 이상"

        elif category == "consecutive_days":
            current_progress = await GoalService._get_consecutive_study_days(
                db, user_id
            )
            progress_percent = min((current_progress / target_value) * 100, 100)
            is_achieved = current_progress >= target_value
            goal_name = f"연속 {target_value}일 학습"

        else:
            return {
                "category": category,
                "error": "지원하지 않는 목표 카테고리입니다"
            }

        return {
            "category": category,
            "goal_name": goal_name,
            "target_value": target_value,
            "current_progress": current_progress,
            "progress_percent": round(progress_percent, 1),
            "is_achieved": is_achieved
        }

    @staticmethod
    async def _get_daily_problem_count(
        db: AsyncSession,
        user_id: int,
        today: date
    ) -> int:
        """
        오늘 사용자가 푼 문제 개수를 조회합니다.
        """
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())

        stmt = select(func.count(UserQuestionTracker.id)).select_from(
            UserQuestionTracker
        ).join(
            TestTracker,
            UserQuestionTracker.study_tracker_id == TestTracker.id
        ).where(
            and_(
                TestTracker.user_id == user_id,
                TestTracker.solved_at >= today_start,
                TestTracker.solved_at <= today_end
            )
        )

        result = await db.execute(stmt)
        count = result.scalar() or 0
        return int(count)

    @staticmethod
    async def _get_daily_accuracy(
        db: AsyncSession,
        user_id: int,
        today: date
    ) -> tuple[float, float]:
        """
        오늘 사용자의 정답률을 조회합니다.

        Returns:
            (정답률, 진행률 백분위)
        """
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())

        # 오늘 푼 문제 중 정답 개수
        correct_stmt = select(func.count(UserQuestionTracker.id)).select_from(
            UserQuestionTracker
        ).join(
            TestTracker,
            UserQuestionTracker.study_tracker_id == TestTracker.id
        ).where(
            and_(
                TestTracker.user_id == user_id,
                TestTracker.solved_at >= today_start,
                TestTracker.solved_at <= today_end,
                UserQuestionTracker.is_correct == True
            )
        )

        # 오늘 푼 문제 총 개수
        total_stmt = select(func.count(UserQuestionTracker.id)).select_from(
            UserQuestionTracker
        ).join(
            TestTracker,
            UserQuestionTracker.study_tracker_id == TestTracker.id
        ).where(
            and_(
                TestTracker.user_id == user_id,
                TestTracker.solved_at >= today_start,
                TestTracker.solved_at <= today_end
            )
        )

        correct_result = await db.execute(correct_stmt)
        total_result = await db.execute(total_stmt)

        correct_count = correct_result.scalar() or 0
        total_count = total_result.scalar() or 0

        if total_count == 0:
            return 0.0, 0.0

        accuracy = (correct_count / total_count) * 100
        return accuracy, accuracy

    @staticmethod
    async def _get_consecutive_study_days(
        db: AsyncSession,
        user_id: int
    ) -> int:
        """
        사용자의 현재 연속 학습일을 계산합니다.
        monthly_study_date를 이용합니다.
        """
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not user.monthly_study_date:
            return 0

        # monthly_study_date가 dict 형태라면 None 반환
        if isinstance(user.monthly_study_date, dict):
            return 0

        # 학습 날짜들을 정렬
        study_dates = sorted(user.monthly_study_date)
        if not study_dates:
            return 0

        # 마지막 날짜부터 역순으로 연속 날짜 개수 세기
        today = datetime.now().date()
        consecutive_count = 0

        # 마지막 학습이 오늘이거나 어제여야 연속 학습 중
        last_study_date = datetime.strptime(study_dates[-1], "%Y-%m-%d").date()

        if last_study_date < today - timedelta(days=1):
            # 어제 이전에 마지막 학습했다면 연속 학습이 끊김
            return 0

        # 연속 날짜 개수 세기
        current_date = last_study_date
        for i in range(len(study_dates) - 1, -1, -1):
            study_date = datetime.strptime(study_dates[i], "%Y-%m-%d").date()

            if study_date == current_date:
                consecutive_count += 1
                current_date -= timedelta(days=1)
            else:
                break

        return consecutive_count

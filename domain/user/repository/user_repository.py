from typing import Optional, Dict, Any

from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession
from domain.user.entity import User


class UserRepository:

    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, update_data: Dict[str, Any]) -> User:
        """
        사용자 정보 업데이트 (동적으로 전달된 필드만 업데이트)

        Args:
            db: Database session
            user_id: 사용자 ID
            update_data: 업데이트할 필드와 값의 딕셔너리

        Returns:
            업데이트된 User 객체
        """
        # None이 아닌 값만 업데이트 (단, profile_image는 명시적 삭제를 위해 None 허용)
        filtered_data = {k: v for k, v in update_data.items() if v is not None or k == 'profile_image'}

        if filtered_data:
            await db.execute(
                update(User)
                .where(User.id == user_id)
                .values(**filtered_data)
            )
            await db.commit()

        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one()

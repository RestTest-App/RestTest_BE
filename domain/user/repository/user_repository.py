from typing import Optional

from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession
from domain.user.entity import User


class UserRepository:

    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, nickname: str, profile_image: Optional[str]) -> User:
            await db.execute(
                update(User)
                .where(User.id == user_id)
                .values(nickname=nickname, profile_image=profile_image)
            )
            await db.commit()
            await db.refresh(User)

            result = await db.execute(select(User).where(User.id == user_id))
            return result.scalar_one()
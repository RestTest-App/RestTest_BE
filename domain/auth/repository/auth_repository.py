from typing import Optional
from domain.user.entity.user import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class AuthRepository:

    # email 조회
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str):
        check = select(User).where(User.email == email)
        exist_user = await db.execute(check)
        return exist_user.scalars().first()


    # 사용자 등록
    @staticmethod
    async def create_user(db: AsyncSession, user: dict):
        new_user = User(**user)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user


    # 사용자 조회
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        return await db.get(User, user_id)
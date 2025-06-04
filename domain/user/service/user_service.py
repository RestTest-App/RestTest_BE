from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependency import get_current_user


class UserService:

    @staticmethod
    async def get_user_from_access_token(token: str, db: AsyncSession) -> dict:
        user = get_current_user(db, token)
        return user


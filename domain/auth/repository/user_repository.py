from typing import Optional
from sqlalchemy.orm import Session
from domain.user.entity.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        return await self.db.get(User, user_id)
from sqlalchemy.ext.asyncio import AsyncSession

from domain.auth.repository.user_repository import UserRepository
from exception.client_exception import NotFoundException

class UserService:

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int):
        user = await UserRepository.get_user_by_id(db, user_id)
        if not user:
            raise NotFoundException(message="사용자를 찾을 수 없습니다.")
from sqlalchemy.ext.asyncio import AsyncSession

from domain.auth.repository.auth_repository import AuthRepository
from domain.auth.service.auth_service import AuthService
from exception.client_exception import UnauthorizedException


class SignInUseCase:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute(self, auth_provider: str, email: str):
        user = await AuthRepository.get_user_by_email_and_provider(self.db, auth_provider, email)
        if not user:
            raise UnauthorizedException(message="등록된 소셜 계정이 아닙니다.")
        return user
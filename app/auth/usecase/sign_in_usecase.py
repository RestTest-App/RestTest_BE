from sqlalchemy.ext.asyncio import AsyncSession

from domain.auth.repository.auth_repository import AuthRepository
from domain.auth.service.kakao_auth_service import KakaoAuthService
from exception.client_exception import UnauthorizedException


class SignInUseCase:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute(self, code: str):
        kakao_service = KakaoAuthService()
        info = await kakao_service.fetch_kakao_user_info(code)
        user = await AuthRepository.get_user_by_email_and_provider(
            self.db,
            auth_provider=info["auth_provider"],
            email=info["email"]
        )
        if not user:
            raise UnauthorizedException(message="등록된 소셜 계정이 아닙니다.")
        return user

    # auth test용
    async def execute_test(self, code: str):
        kakao_service = KakaoAuthService()
        info = await kakao_service.fetch_user_into_test(code)
        user = await AuthRepository.get_user_by_email_and_provider(
            self.db,
            auth_provider=info["auth_provider"],
            email=info["email"]
        )
        if not user:
            raise UnauthorizedException(message="등록된 소셜 계정이 아닙니다.")
        return user

from typing import Dict
from core.config import settings
from domain.auth.repository.token_repository import TokenRepository
from domain.auth.service.jwt_service import JWTService


class TokenUseCase:

    def __init__(
            self,
            token_repository: TokenRepository = TokenRepository(),
            jwt_service: JWTService = JWTService()
    ):
        self.token_repository = token_repository
        self.jwt_service = jwt_service
        self.refresh_ttl = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600


    async def generate_tokens(self, user_id: int) -> Dict[str, str]:
        access_token = self.jwt_service.create_access_token(user_id=user_id)
        refresh_token, jti = self.jwt_service.create_refresh_token(user_id=user_id)
        expire = self.refresh_ttl

        await self.token_repository.save_jti(
            user_id=user_id,
            jti=jti,
            expire_seconds=expire
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }

from typing import Dict
from jose import ExpiredSignatureError, JWTError
from core.config import settings
from domain.auth.repository.token_repository import TokenRepository
from domain.auth.service.jwt_service import JWTService
from exception.client_exception import UnauthorizedException, BadRequestException, NotFoundException, ForbiddenException


class RefreshTokenRotationUseCase:

    def __init__(
            self,
            token_repository: TokenRepository = TokenRepository(),
            jwt_service: JWTService = JWTService(),
    ):
        self.token_repository = token_repository
        self.jwt_service = jwt_service
        self.refresh_ttl = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600


    async def execute(self, raw_refresh_token: str) -> Dict[str, str]:
        try:
            payload = self.jwt_service.verify_token(raw_refresh_token)
            print("[DEBUG] payload:", payload)
        except ExpiredSignatureError:
            raise UnauthorizedException(message="리프레시 토큰이 만료되었습니다.")
        except JWTError:
            raise BadRequestException(message="유효하지 않은 리프레시 토큰입니다.")

        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise BadRequestException(message="사용자 정보가 없습니다.")
        user_id = int(user_id_str)

        incoming_jti = payload.get("jti")
        if not incoming_jti:
            raise BadRequestException(message="jwi가 없습니다.")

        print(f"[DEBUG] user_id: {user_id}")
        print(f"[DEBUG] incoming_jti from token: {incoming_jti}")

        stored_jti = await self.token_repository.get_jti(user_id=user_id)
        if stored_jti is None:
            raise NotFoundException(message="저장된 리프레시 토큰이 없습니다. 다시 로그인 해주세요.")
        print(f"[DEBUG] stored_jti from redis: {stored_jti}")


        if stored_jti != incoming_jti:
            await self.token_repository.delete_jti(user_id=user_id)
            raise ForbiddenException(message="리프레시 토큰 재사용이 감지되었습니다. 해당 사용자를 로그아웃합니다.")

        new_refresh_token, new_jti = self.jwt_service.create_refresh_token(user_id=user_id)
        await self.token_repository.save_jti(
            user_id=user_id,
            jti=new_jti,
            expire_seconds=self.refresh_ttl
        )

        new_access_token = self.jwt_service.create_access_token(user_id=user_id)

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
        }
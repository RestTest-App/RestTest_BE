from domain.auth.repository.token_repository import TokenRepository
from domain.auth.service.jwt_service import JWTService
from exception.client_exception import BadRequestException


class SignOutUseCase:

    def __init__(
            self,
            jwt_service: JWTService = JWTService(),
            token_repository: TokenRepository = TokenRepository()
    ):
        self.jwt_service = jwt_service
        self.token_repository = token_repository

    async def execute(self, refresh_token: str):
        try:
            payload = self.jwt_service.verify_token(refresh_token)
        except Exception:
            raise BadRequestException(message="유효하지 않은 리프레시 토큰입니다.")

        user_id = payload.get("sub")
        if not user_id:
            raise BadRequestException(message="토큰에 사용자 정보가 없습니다.")

        await self.token_repository.delete_jti(user_id=int(user_id))
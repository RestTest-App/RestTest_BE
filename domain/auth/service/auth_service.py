from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dto.request import SignUpRequest
from domain.auth.dto.user_create_dto import UserCreateDTO
from domain.auth.repository.auth_repository import AuthRepository
from exception.client_exception import NotFoundException, ForbiddenException, ConfilctException
from datetime import datetime, timezone


class AuthService:

    # 사용자 등록
    @staticmethod
    async def create_user(db: AsyncSession, dto: UserCreateDTO):
        exist_user = await AuthRepository.get_by_email(db, dto.email)
        if exist_user:
            raise ConfilctException(message="이미 등록된 사용자입니다.") # 409

        if not dto.agree_to_terms:
            raise ForbiddenException(message="약관 동의가 필요합니다.") # 403

        data = dto.model_dump(
            exclude={"certificates"},
            exclude_none=True
        )
        data.setdefault("created_at", datetime.now(timezone.utc))

        user = await AuthRepository.create_user(db, data)
        return user


    # id로 사용자 조회
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int):
        user = await AuthRepository.get_user_by_id(db, user_id)
        if not user:
            raise NotFoundException(message="사용자를 찾을 수 없습니다.") # 404
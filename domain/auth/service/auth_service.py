from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from domain.auth.service.jwt_service import JWTService
from domain.auth.dto.user_create_dto import UserCreateDTO
from domain.auth.repository.auth_repository import AuthRepository
from domain.user.entity import User
from domain.user.repository.certificate_repository import CertificateRepository
from exception.client_exception import NotFoundException, ForbiddenException, ConflictException
from datetime import datetime
from zoneinfo import ZoneInfo

class AuthService:

    _jwt_service = JWTService()

    # 사용자 등록
    @staticmethod
    async def create_user(db: AsyncSession, dto: UserCreateDTO):
        # 이메일 중복 검사
        exist_user = await AuthRepository.get_by_email(db, dto.email)
        if exist_user:
            raise ConflictException(message="이미 등록된 사용자입니다.")  # 409

        # 약관 동의
        if not dto.agree_to_terms:
            raise ForbiddenException(message="약관 동의가 필요합니다.")  # 403

        data = dto.model_dump(
            exclude={"certificates"},
            exclude_none=True
        )
        data.setdefault("created_at", datetime.now(ZoneInfo("Asia/Seoul"))).isoformat()
        user = await AuthRepository.create_user(db, data)

        if dto.certificates:
            user = await CertificateRepository.add_user_certificate(db, user, dto.certificates)

        return user

    # id로 사용자 조회
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
        user: Optional[User] = await AuthRepository.get_user_by_id(db, user_id)
        if not user:
            raise NotFoundException(message="사용자를 찾을 수 없습니다.")  # 404
        return user
    

    # 회원탈퇴
    @staticmethod
    async def delete_account(user_id: int, db: AsyncSession) -> None:
        user = await AuthRepository.get_user_by_id(db, user_id)
        if not user:
            raise NotFoundException(message="사용자를 찾을 수 없습니다.")
        await AuthRepository.delete_user(db, user)
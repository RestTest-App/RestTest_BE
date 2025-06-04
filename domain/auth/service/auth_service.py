from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from core.security import JWTService
from domain.auth.dto.user_create_dto import UserCreateDTO
from domain.auth.repository.auth_repository import AuthRepository
from domain.auth.repository.token_repository import TokenStore, token_store
from domain.user.entity import User
from domain.user.repository.certificate_repository import CertificateRepository
from exception.client_exception import NotFoundException, ForbiddenException, ConfilctException
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

class AuthService:

    _jwt_service = JWTService()

    # 사용자 등록
    @staticmethod
    async def create_user(db: AsyncSession, dto: UserCreateDTO):
        # 이메일 중복 검사
        exist_user = await AuthRepository.get_by_email(db, dto.email)
        if exist_user:
            raise ConfilctException(message="이미 등록된 사용자입니다.") # 409

        # 약관 동의
        if not dto.agree_to_terms:
            raise ForbiddenException(message="약관 동의가 필요합니다.") # 403


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
    async def get_user(db: AsyncSession, user_id: int) -> User:
        user: Optional[User] = await AuthRepository.get_user_by_id(db, user_id)
        if not user:
            raise NotFoundException(message="사용자를 찾을 수 없습니다.") # 404
        return user


    # 로그아웃
    @staticmethod
    async def sign_out(refresh_token: str, store: TokenStore = token_store) -> None:
        jwt_service = JWTService()
        jwt_service.verify_token(refresh_token)
        if await store.is_revoked(refresh_token):
            return
        await store.revoke(refresh_token)

    # 회원탈퇴
    @staticmethod
    async def delete_account(user_id: int, db: AsyncSession) -> None:
        user = await AuthRepository.get_user_by_id(db, user_id)
        if not user:
            raise NotFoundException(message="사용자를 찾을 수 없습니다.")
        await AuthRepository.delete_user(db, user)
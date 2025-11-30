from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.user.dto.request.update_user_profile_request import UpdateUserProfileRequest
from domain.user.entity.user import User
from domain.user.repository.user_repository import UserRepository
from domain.user.service.user_service import UserService
from exception.client_exception import ForbiddenException


class UpdateUserProfileUseCase:
    """사용자 프로필(닉네임, 이미지) 수정 UseCase"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_service = UserService()

    async def execute(
        self,
        user: User,
        request: UpdateUserProfileRequest,
        profile_image: UploadFile = None
    ) -> User:
        """
        사용자 프로필 업데이트 실행

        Args:
            user: 현재 로그인한 사용자 (from get_current_user)
            request: 업데이트 요청 DTO (nickname, delete_image)
            profile_image: 업로드할 프로필 이미지 파일

        Returns:
            업데이트된 User 객체

        Raises:
            ForbiddenException: 권한 없음 (다른 사용자 수정 시도)
        """
        update_data = {}

        # 닉네임 업데이트
        if request.nickname:
            update_data['nickname'] = request.nickname

        # 프로필 이미지 처리
        if profile_image:
            # 기존 이미지 삭제
            if user.profile_image:
                self.user_service.delete_profile_image(user.profile_image)

            # 새 이미지 업로드
            image_url = await self.user_service.upload_profile_image(profile_image)
            update_data['profile_image'] = image_url

        elif request.delete_image:
            # 이미지 삭제 요청
            if user.profile_image:
                self.user_service.delete_profile_image(user.profile_image)
            update_data['profile_image'] = None

        # 데이터베이스에 업데이트
        updated_user = await UserRepository.update_user(
            self.db,
            user.id,
            update_data
        )

        return updated_user
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.user.dto.request.update_user_info_request import UpdateUserInfoRequest
from domain.user.entity.user import User
from domain.user.repository.user_repository import UserRepository


class UpdateUserInfoUseCase:
    """사용자 정보(모든 필드) 수정 UseCase"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute(
        self,
        user: User,
        request: UpdateUserInfoRequest
    ) -> User:
        """
        사용자 정보 업데이트 실행 (JSON으로 여러 필드 동시 수정)

        Args:
            user: 현재 로그인한 사용자 (from get_current_user)
            request: 업데이트 요청 DTO (nickname, gender, birthday, job, rest_goal, test_goal, goal_table)

        Returns:
            업데이트된 User 객체

        Raises:
            ValidationError: 필드 검증 실패
        """
        # request에서 None이 아닌 값만 추출
        update_data = request.model_dump(exclude_none=True)

        # birthday는 string → datetime으로 변환 필요
        if 'birthday' in update_data and isinstance(update_data['birthday'], str):
            try:
                update_data['birthday'] = datetime.strptime(update_data['birthday'], '%Y-%m-%d').date()
            except ValueError:
                # 이미 validator에서 검증했으므로 여기서는 그냥 진행
                pass

        # goal_table은 list → dict 또는 list 형식으로 저장
        # DB에 JSON으로 저장되므로 리스트 그대로 유지
        if 'goal_table' in update_data:
            update_data['goal_table'] = update_data['goal_table']

        # 데이터베이스에 업데이트
        updated_user = await UserRepository.update_user(
            self.db,
            user.id,
            update_data
        )

        return updated_user
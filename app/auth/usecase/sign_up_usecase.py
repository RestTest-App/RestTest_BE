from sqlalchemy.ext.asyncio import AsyncSession

from domain.auth.dto.user_create_dto import UserCreateDTO
from domain.auth.service.auth_service import AuthService


class SignUpUseCase:

    def __init__(self, db: AsyncSession):
        self.db = db


    async def execute(self, dto: UserCreateDTO):
        return await AuthService.create_user(self.db, dto)
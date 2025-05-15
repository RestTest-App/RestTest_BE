from sqlalchemy.ext.asyncio import AsyncSession

from core.security import verify_access_token
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends

from database.dependency import get_db
from domain.auth.service.user_service import UserService
from exception.client_exception import UnauthorizedException

# Auth 의존성
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db())
):
    payload = verify_access_token(token)
    user_id = payload.get("sub")

    if user_id is None:
        raise UnauthorizedException(detail="사용자 정보가 없습니다.")

    user_id = payload.get("sub")
    user = UserService.get_user_by_id(db, int(user_id))

    return user
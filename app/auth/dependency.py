from typing import Dict

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends

from database.dependency import get_db
from domain.auth.service.auth_service import AuthService
from exception.client_exception import UnauthorizedException, NotFoundException
from core.security import JWTService

# Auth 의존성
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# access token 디코딩 후 사용자 정보 load
async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
):
    jwt_service = JWTService()

    # access token 디코딩 후 dict으로 token 정보 가져오기
    payload: Dict = jwt_service.verify_token(token)

    # payload에서 id에 해당하는 값 가져오기
    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException(message="사용자 정보가 없습니다.")

    # 사용자 데이터 가져오기
    user = await AuthService.get_user(db, int(user_id))
    if not user:
        raise NotFoundException(message="사용자를 찾을 수 없습니다.")

    return user

async def get_bearer_token(token: str = Depends(oauth2_scheme)) -> str:
    return token

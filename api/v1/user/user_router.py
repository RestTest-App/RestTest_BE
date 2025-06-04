from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependency import get_current_user
from app.user.dto.response.get_user_info_response import GetUserInfoResponse
from core.security import JWTService

router = APIRouter(prefix='/api/v1/user', tags=["user"])

jwt_service = JWTService()


# 사용자 정보 조회
@router.get("/get-user-info", response_model=GetUserInfoResponse)
async def get_user_info(user=Depends(get_current_user)):
    return GetUserInfoResponse.model_validate(user)

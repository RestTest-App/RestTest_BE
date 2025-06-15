from fastapi import APIRouter
from fastapi.params import Depends

from app.auth.dependency import get_current_user
from app.user.dto.response.get_user_info_response import GetUserInfoResponse
from app.user.dto.response.update_user_info_response import UpdateUserInfoResponse
from core.security import JWTService
from exception.success import ok

router = APIRouter()

jwt_service = JWTService()


# 사용자 정보 조회
@router.get("/get-user-info", response_model=GetUserInfoResponse)
async def get_user_info(user=Depends(get_current_user)):
    user_info = GetUserInfoResponse.model_validate(user)
    payload: dict = user_info.model_dump(mode="json")
    return ok(data=payload, message="사용자 정보 조회 성공")

@router.patch("/update-user-info", response_model=UpdateUserInfoResponse)
async def update_user_info():
    pass

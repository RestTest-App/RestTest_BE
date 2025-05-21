from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dto.request import SignUpRequest, SignInRequest
from app.auth.dto.response.sign_in_response import SignInResponse
from app.auth.dto.response.sign_up_response import SignUpResponse
from app.auth.usecase.sign_in_usecase import SignInUseCase
from app.auth.usecase.sign_up_usecase import SignUpUseCase
from core.security import JWTService
from database.dependency import get_db
from domain.auth.dto.user_create_dto import UserCreateDTO
from exception.success import created

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
jwt_service = JWTService()

@router.post("/sign-up", response_model=SignUpResponse)
async def sign_up(request: SignUpRequest, db: AsyncSession = Depends(get_db)):
    dto = UserCreateDTO(**request.model_dump())
    usecase = SignUpUseCase(db)
    user = await usecase.execute(dto)
    data = {"sub": str(user.id)}
    access_token = jwt_service.create_access_token(data)
    refresh_token = jwt_service.create_refresh_token(data)

    token_data = {"access_token": access_token, "refresh_token": refresh_token}
    return created(data=token_data, message="회원가입 성공")

@router.post("/sign-in", response_model=SignInResponse)
async def sign_in(request: SignInRequest, db: AsyncSession = Depends(get_db)):
    user = await SignInUseCase(db).execute(request.auth_provider, request.email)
    payload = {"sub": str(user.id)}
    access_token = jwt_service.create_access_token(payload)
    refresh_token = jwt_service.create_refresh_token(payload)

    return created(
        data = {
            "access_token": access_token,
            "refresh_token": refresh_token
        },
        message="로그인 성공"
    )
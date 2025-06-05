from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dto.request import SignUpRequest, SignInRequest
from app.auth.dto.request.sign_out_request import SignOutRequest
from app.auth.dto.response.sign_in_response import SignInResponse
from app.auth.dto.response.sign_up_response import SignUpResponse
from app.auth.usecase.sign_in_usecase import SignInUseCase
from app.auth.usecase.sign_up_usecase import SignUpUseCase
from core.security import JWTService
from database.dependency import get_db
from domain.auth.dto.user_create_dto import UserCreateDTO
from domain.auth.repository.token_repository import TokenStore, token_store
from domain.auth.service.auth_service import AuthService
from domain.auth.service.kakao_auth_service import KakaoAuthService
from exception.success import created, ok, no_content

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

jwt_service = JWTService()

def get_token_store() -> TokenStore:
    return token_store

# 카카오 회원가입
@router.post("/sign-up", response_model=SignUpResponse)
async def sign_up(request: SignUpRequest, db: AsyncSession = Depends(get_db)):
    # 카카오에서 정보 받아오기 (email, auth_provider)
    info = await KakaoAuthService().fetch_kakao_user_info(code=request.code)

    # 카카오 인가 코드 추가
    data = request.model_dump(exclude={"code"})
    data.update(info)

    dto = UserCreateDTO(**data)
    usecase = SignUpUseCase(db)
    user = await usecase.execute(dto)

    # token 발급
    payload = {"sub" : str(user.id)}
    access_token = jwt_service.create_access_token(payload)
    refresh_token = jwt_service.create_refresh_token(payload)

    token_data = {
        "access_token" : access_token,
        "refresh_token" : refresh_token,
    }

    return created(data=token_data, message="회원가입 성공")


@router.post("/sign-in", response_model=SignInResponse)
async def sign_in(request: SignInRequest, db: AsyncSession = Depends(get_db)):

    usecase = SignInUseCase(db)
    user = await usecase.execute(request.code)

    payload = {"sub": str(user.id)}
    access_token = jwt_service.create_access_token(payload)
    refresh_token = jwt_service.create_refresh_token(payload)

    token_data = {
        "access_token" : access_token,
        "refresh_token" : refresh_token,
    }

    return created(data = token_data, message="로그인 성공")

@router.post("/sign-out")
async def sign_out(request: SignOutRequest, store: TokenStore = Depends(get_token_store)):
    await AuthService.sign_out(request.refresh_token, store)
    return ok(data=None, message="로그아웃 성공")

@router.delete("/delete-account")
async def delete_account(user_id: int, db: AsyncSession = Depends(get_db)):
    await AuthService.delete_account(user_id, db)
    return no_content()












# test api


@router.post("/sign-up-test", response_model=SignUpResponse)
async def sign_up_test(request: SignUpRequest, db: AsyncSession = Depends(get_db)):
    info = await KakaoAuthService().fetch_user_into_test(code=request.code)

    # 카카오 인가 코드 추가
    data = request.model_dump(exclude={"code"})
    data.update(info)

    dto = UserCreateDTO(**data)
    usecase = SignUpUseCase(db)
    user = await usecase.execute(dto)

    # token 발급
    payload = {"sub" : str(user.id)}
    access_token = jwt_service.create_access_token(payload)
    refresh_token = jwt_service.create_refresh_token(payload)

    token_data = {
        "access_token" : access_token,
        "refresh_token" : refresh_token,
    }

    return created(data=token_data, message="회원가입 성공")



@router.post("/sign-in-test", response_model=SignInResponse)
async def sign_in(request: SignInRequest, db: AsyncSession = Depends(get_db)):

    usecase = SignInUseCase(db)
    user = await usecase.execute_test(request.code)

    payload = {"sub": str(user.id)}
    access_token = jwt_service.create_access_token(payload)
    refresh_token = jwt_service.create_refresh_token(payload)

    token_data = {
        "access_token" : access_token,
        "refresh_token" : refresh_token,
    }

    return created(data = token_data, message="로그인 성공")
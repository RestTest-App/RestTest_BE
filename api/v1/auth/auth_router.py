from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependency import get_current_user, get_bearer_token
from app.auth.dto.request import SignUpRequest, SignInRequest
from app.auth.dto.response.issue_tokens_response import IssueTokensResponseDto
from app.auth.dto.response.sign_in_response import SignInResponse
from app.auth.dto.response.sign_up_response import SignUpResponse
from app.auth.usecase.refresh_token_rotation_usecase import RefreshTokenRotationUseCase
from app.auth.usecase.sign_in_usecase import SignInUseCase
from app.auth.usecase.sign_out_usecase import SignOutUseCase
from app.auth.usecase.sign_up_usecase import SignUpUseCase
from app.auth.usecase.token_usecase import TokenUseCase
from domain.auth.service.jwt_service import JWTService
from database.dependency import get_db
from domain.auth.dto.user_create_dto import UserCreateDTO
from domain.auth.service.auth_service import AuthService
from domain.auth.service.kakao_auth_service import KakaoAuthService

from app.utils.dto.success import created, ok, no_content
from exception.client_exception import BadRequestException

router = APIRouter()

jwt_service = JWTService()

def get_sign_out_usecase() -> SignOutUseCase:
    return SignOutUseCase()

def get_refresh_token_usecase() -> RefreshTokenRotationUseCase:
    return RefreshTokenRotationUseCase()



# 카카오 회원가입
@router.post("/sign-up", response_model=SignUpResponse)
async def sign_up(request: SignUpRequest, db: AsyncSession = Depends(get_db)):
    # 카카오에서 정보 받아오기 (email, auth_provider)
    info = await KakaoAuthService().fetch_kakao_user_info(kakao_token=request.kakao_token)
    print(info.values())

    user_dto = UserCreateDTO(
        **{**request.model_dump(exclude={"kakao_token"}), **info}
    )

    user = await SignUpUseCase(db).execute(user_dto)
    token_data = TokenUseCase.generate_tokens(user_id=user.id)

    return created(data=token_data, message="회원가입 성공")


# 로그인
@router.post("/sign-in", response_model=SignInResponse)
async def sign_in(request: SignInRequest, db: AsyncSession = Depends(get_db)):

    info = await KakaoAuthService().fetch_kakao_user_info(kakao_token=request.kakao_token)
    user = await SignInUseCase(db).execute(
        email=info["email"],
        auth_provider="KAKAO"
    )

    token_data = await TokenUseCase().generate_tokens(user_id=user.id)

    return created(data = token_data, message="로그인 성공")


# 로그아웃
@router.post("/sign-out")
async def sign_out(
    raw_refresh_token: str = Depends(get_bearer_token),
    usecase: SignOutUseCase = Depends(get_sign_out_usecase)
):
    await usecase.execute(raw_refresh_token)
    return ok(message="로그아웃 완료", data=None)


# 회원탈퇴
@router.delete("/delete-account")
async def delete_account(user_id: int, db: AsyncSession = Depends(get_db)):
    await AuthService.delete_account(user_id, db)
    return no_content()


# access token 재발급
@router.put("/refresh-token", response_model=IssueTokensResponseDto)
async def refresh_token(
        raw_refresh_token: str = Depends(get_bearer_token),
        usecase: RefreshTokenRotationUseCase = Depends(get_refresh_token_usecase)
):
    tokens = await usecase.execute(raw_refresh_token)

    return ok(data=tokens, message="액세스 토큰 발급 완료")





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
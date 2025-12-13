from typing import Dict

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends

from database.dependency import get_db
from domain.auth.service.auth_service import AuthService
from exception.client_exception import UnauthorizedException, NotFoundException, RateLimitExceededException
from domain.auth.service.jwt_service import JWTService
from domain.rate_limit.service.rate_limit_service import RateLimitService
from domain.user.entity.user import User

# Auth 의존성
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# access token 디코딩 후 사용자 정보 load
async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
):
    payload = JWTService.verify_token(token)
    user_id = payload.get("sub")
    print(f"Decoded token user_id (sub): {user_id}")
    jwt_service = JWTService()

    payload: Dict = jwt_service.verify_token(token)

    user = await AuthService.get_user_by_id(db, int(user_id))

    if user is None:
        raise UnauthorizedException(detail="유효하지 않은 사용자입니다.")  # ★ 이 부분 추가
    # payload에서 id에 해당하는 값 가져오기
    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException(message="사용자 정보가 없습니다.")

    # 사용자 데이터 가져오기
    user = await AuthService.get_user_by_id(db, int(user_id))
    if not user:
        raise NotFoundException(message="사용자를 찾을 수 없습니다.")

    return user

async def get_bearer_token(token: str = Depends(oauth2_scheme)) -> str:
    return token


# Rate Limit 체크 의존성 (체크만 하고 증가는 안함)
async def check_api_rate_limit(
    current_user: User = Depends(get_current_user)
):
    """
    API 호출 제한 체크 (카운트 증가 없음)

    사용자의 멤버십 등급에 따라 일일 API 호출 횟수를 제한합니다.
    - FREE: 5회/일
    - PREMIUM: 1000회/일 (사실상 무제한)

    실제 카운트 증가는 RateLimitMiddleware에서 응답 성공 시에만 수행됩니다.

    Raises:
        RateLimitExceededException: 일일 제한 횟수 초과 시
    """
    rate_limiter = RateLimitService()

    try:
        # membership_tier가 없으면 기본값 'FREE' 사용
        membership_tier = getattr(current_user, 'membership_tier', 'FREE')

        # 현재 사용량 체크만 수행
        can_proceed = await rate_limiter.check_rate_limit(
            user_id=current_user.id,
            membership_tier=membership_tier
        )

        if not can_proceed:
            # 제한 정보 가져오기
            limit_info = await rate_limiter.get_limit_info(
                user_id=current_user.id,
                membership_tier=membership_tier
            )

            raise RateLimitExceededException(
                message=f"일일 무료 사용 횟수({limit_info['limit']}회)를 초과했습니다. 프리미엄 구독을 이용해주세요."
            )

        # 사용량 증가는 하지 않음 - Middleware에서 처리

    finally:
        await rate_limiter.close()

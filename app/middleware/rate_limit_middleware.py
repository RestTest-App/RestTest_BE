"""
Rate Limit Middleware
응답이 성공(2xx)일 때만 API 사용량 카운트를 증가시킵니다.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from domain.rate_limit.service.rate_limit_service import RateLimitService
from domain.auth.service.jwt_service import JWTService
from domain.auth.service.auth_service import AuthService
from database.session import AsyncSessionLocal


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate Limit Middleware

    특정 경로에 대해 응답이 성공(2xx)일 때만 사용량을 증가시킵니다.
    """

    # Rate limit을 적용할 경로 패턴
    RATE_LIMITED_PATHS = [
        "/api/v1/studybook/upload-my-studybook",
        # 필요시 다른 경로 추가
    ]

    async def dispatch(self, request: Request, call_next):
        """요청 처리 및 응답 후 rate limit 증가"""

        # 응답 받기
        response: Response = await call_next(request)

        # Rate limit 대상 경로인지 확인
        if not any(request.url.path.startswith(path) for path in self.RATE_LIMITED_PATHS):
            return response

        # 응답이 성공(2xx)인지 확인
        if not (200 <= response.status_code < 300):
            return response

        # Authorization 헤더에서 토큰 추출
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return response

        token = auth_header.replace("Bearer ", "")

        try:
            # 토큰에서 사용자 ID 추출
            jwt_service = JWTService()
            payload = jwt_service.verify_token(token)
            user_id = payload.get("sub")

            if not user_id:
                return response

            # 사용자 정보 조회 (membership_tier 확인용)
            async with AsyncSessionLocal() as db:
                user = await AuthService.get_user_by_id(db, int(user_id))

                if not user:
                    return response

                # Rate limit 증가
                rate_limiter = RateLimitService()
                try:
                    await rate_limiter.increment_usage(int(user_id))
                finally:
                    await rate_limiter.close()

        except Exception as e:
            # 에러 발생 시 로깅만 하고 응답은 정상 반환
            print(f"[RateLimitMiddleware] Error incrementing usage: {e}")

        return response

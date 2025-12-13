"""
Rate Limit Service
Redis를 이용한 API 호출 횟수 제한 서비스
"""
from datetime import datetime, timedelta
from typing import Optional
import redis.asyncio as redis
from core.config import redis_settings


class RateLimitService:
    """API 호출 제한 서비스"""

    # 등급별 일일 제한 횟수
    TIER_LIMITS = {
        "FREE": 5,
        "PREMIUM": 1000,  # 사실상 무제한
    }

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None

    async def _get_redis(self) -> redis.Redis:
        """Redis 클라이언트 가져오기 (Lazy initialization)"""
        if self.redis_client is None:
            self.redis_client = redis.Redis(
                host=redis_settings.REDIS_HOST,
                port=redis_settings.REDIS_PORT,
                db=0,
                decode_responses=True
            )
        return self.redis_client

    def _get_daily_key(self, user_id: int) -> str:
        """일일 사용량 추적을 위한 Redis 키 생성"""
        today = datetime.now().strftime("%Y-%m-%d")
        return f"rate_limit:user:{user_id}:date:{today}"

    async def check_rate_limit(self, user_id: int, membership_tier: str) -> bool:
        """
        사용자의 API 호출 제한 확인

        Args:
            user_id: 사용자 ID
            membership_tier: 멤버십 등급 (FREE, PREMIUM)

        Returns:
            bool: True면 호출 가능, False면 제한 초과
        """
        limit = self.TIER_LIMITS.get(membership_tier, self.TIER_LIMITS["FREE"])
        current_usage = await self.get_current_usage(user_id)

        return current_usage < limit

    async def get_current_usage(self, user_id: int) -> int:
        """
        오늘 사용한 API 호출 횟수 조회

        Args:
            user_id: 사용자 ID

        Returns:
            int: 오늘 사용한 횟수
        """
        redis_client = await self._get_redis()
        key = self._get_daily_key(user_id)

        usage = await redis_client.get(key)
        return int(usage) if usage else 0

    async def increment_usage(self, user_id: int) -> int:
        """
        API 호출 횟수 증가

        Args:
            user_id: 사용자 ID

        Returns:
            int: 증가 후 총 사용 횟수
        """
        redis_client = await self._get_redis()
        key = self._get_daily_key(user_id)

        # 증가
        new_count = await redis_client.incr(key)

        # 첫 호출이면 만료 시간 설정 (오늘 자정까지)
        if new_count == 1:
            # 오늘 자정까지 남은 시간 계산
            now = datetime.now()
            midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            seconds_until_midnight = int((midnight - now).total_seconds())

            await redis_client.expire(key, seconds_until_midnight)

        return new_count

    async def get_remaining_quota(self, user_id: int, membership_tier: str) -> int:
        """
        남은 API 호출 가능 횟수 조회

        Args:
            user_id: 사용자 ID
            membership_tier: 멤버십 등급

        Returns:
            int: 남은 호출 가능 횟수
        """
        limit = self.TIER_LIMITS.get(membership_tier, self.TIER_LIMITS["FREE"])
        current_usage = await self.get_current_usage(user_id)

        remaining = limit - current_usage
        return max(0, remaining)

    async def get_limit_info(self, user_id: int, membership_tier: str) -> dict:
        """
        사용자의 제한 정보 전체 조회

        Args:
            user_id: 사용자 ID
            membership_tier: 멤버십 등급

        Returns:
            {
                "limit": int,
                "used": int,
                "remaining": int,
                "tier": str
            }
        """
        limit = self.TIER_LIMITS.get(membership_tier, self.TIER_LIMITS["FREE"])
        used = await self.get_current_usage(user_id)
        remaining = max(0, limit - used)

        return {
            "limit": limit,
            "used": used,
            "remaining": remaining,
            "tier": membership_tier
        }

    async def close(self):
        """Redis 연결 종료"""
        if self.redis_client:
            await self.redis_client.close()

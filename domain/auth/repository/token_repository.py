from abc import ABC, abstractmethod

# 1) 추상 인터페이스: TokenStore
class TokenStore(ABC):
    @abstractmethod
    async def revoke(self, token: str) -> None:
        """토큰을 무효화 저장소에 등록합니다."""
        raise NotImplementedError()

    @abstractmethod
    async def is_revoked(self, token: str) -> bool:
        """토큰이 이미 무효화되었는지 확인합니다."""
        raise NotImplementedError()


# 2) Redis 유사 API를 흉내 내는 FakeRedisClient
class FakeRedisClient:
    def __init__(self):
        self._store: dict[str, str] = {}

    async def set(self, key: str, value: str, ex=None) -> None:
        self._store[key] = value

    async def exists(self, key: str) -> int:
        return 1 if key in self._store else 0


fake_redis = FakeRedisClient()


# 3) TokenStore 추상인터페이스를 구현하는 클래스
class RedisLikeTokenStore(TokenStore):
    def __init__(self, redis_client: FakeRedisClient):
        self.client = redis_client

    async def revoke(self, token: str) -> None:
        # Redis set(key, value)
        await self.client.set(token, "revoked")

    async def is_revoked(self, token: str) -> bool:
        # Redis exists(key)
        return await self.client.exists(token) == 1


# 4) DI용 인스턴스 생성
#    클래스가 아니라, 위에서 정의한 RedisLikeTokenStore를 인자로 넘겨야 합니다.
token_store = RedisLikeTokenStore(fake_redis)
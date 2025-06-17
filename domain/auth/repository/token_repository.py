from core.redis import redis_client


class TokenRepository:

    # jti : jwt token id
    PREFIX = 'refresh_jti:'

    # jti 불러오기
    @staticmethod
    async def get_jti(user_id: int) -> str:
        key = TokenRepository.PREFIX + str(user_id)
        return await redis_client.get(key)

    # jti 저장 + ttl 설정
    @staticmethod
    async def save_jti(user_id: int, jti: str, expire_seconds: int) -> None:
        key = TokenRepository.PREFIX + str(user_id)
        await redis_client.setex(key, expire_seconds, jti)

    # jti 삭제
    @staticmethod
    async def delete_jti(user_id: int):
        key = TokenRepository.PREFIX + str(user_id)
        await redis_client.delete(key)
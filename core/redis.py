from redis.asyncio import Redis
from core.config import redis_settings

redis_client = Redis(
    host = redis_settings.REDIS_HOST,
    port = redis_settings.REDIS_PORT,
    db = 0,
    decode_responses = True
)
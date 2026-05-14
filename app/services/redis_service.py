import redis.asyncio as redis
from app.core.config import settings

class RedisService:
    def __init__(self):
        self.redis_client: redis.Redis = None

    async def connect(self):
        """Initialize asynchronous Redis connection."""
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )

    async def disconnect(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()

    async def blacklist_token(self, jti: str, expire_seconds: int):
        """Add a token identifier to the blacklist with a TTL."""
        await self.redis_client.setex(f"blacklist:{jti}", expire_seconds, "1")

    async def is_token_blacklisted(self, jti: str) -> bool:
        """Check if a token identifier exists in the blacklist."""
        return await self.redis_client.exists(f"blacklist:{jti}") > 0

redis_service = RedisService()

async def get_redis():
    """Dependency to get Redis client."""
    return redis_service.redis_client

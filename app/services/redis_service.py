import asyncio
import redis.asyncio as redis
from app.core.config import settings

class RedisService:
    def __init__(self):
        self.redis_client: redis.Redis = None

    async def connect(self):
        """Initialize asynchronous Redis connection with hard-fail logic."""
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=0.1,
                socket_timeout=0.1,
                retry_on_timeout=False
            )
            # Hard check: If it doesn't ping instantly, we disable it
            await asyncio.wait_for(self.redis_client.ping(), timeout=0.2)
            print("✅ Redis connection established (Zero-Trust Active)")
        except Exception:
            print("⚠️ Redis not found. Disabling Zero-Trust cache for this session (Failsafe Active)")
            self.redis_client = None

    async def disconnect(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()

    async def blacklist_token(self, jti: str, expire_seconds: int):
        if not self.redis_client:
            return
        try:
            await self.redis_client.setex(f"blacklist:{jti}", expire_seconds, "1")
        except Exception as e:
            print(f"Redis Warning: Could not blacklist token: {e}")

    async def is_token_blacklisted(self, token: str) -> bool:
        if not self.redis_client:
            return False
        try:
            # v1.4.2: We check if the token (or its hash) exists in the blacklist
            return await self.redis_client.exists(f"blacklist:{token}") > 0
        except Exception as e:
            print(f"Redis Warning: Could not check blacklist (is Redis running?): {e}")
            return False

redis_service = RedisService()

async def get_redis():
    """Dependency to get Redis client."""
    return redis_service.redis_client

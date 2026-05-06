import secrets

from cachetools import TTLCache
from redis.asyncio import Redis

from .redis_client import RedisClient
from .redis_config import redis_config


class RedisTokenizer:
    _instance: RedisTokenizer | None = None
    _token_cache = TTLCache(maxsize=10000, ttl=300)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.redis: Redis | None = None

    async def get_token(self, user_id: int):
        if self.redis is None:
            self.redis = await RedisClient.get_client()

        cached = self._token_cache.get(user_id, None)
        if cached:
            return cached

        token = secrets.token_hex(16)
        token_key = f"{redis_config.key_prefix}:anon_token:{token}"

        await self.redis.set(token_key, user_id, ex=60)
        self._token_cache[user_id] = token

        return token

    async def _get_user_id(self, token: str) -> int:
        if self.redis is None:
            self.redis = await RedisClient.get_client()

        token_key = f"{redis_config.key_prefix}:anon_token:{token}"

        user_id = await self.redis.get(token_key)
        return int(user_id) if user_id else None

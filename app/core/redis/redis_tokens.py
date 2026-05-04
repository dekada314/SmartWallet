import secrets

from cachetools import TTLCache
from redis.asyncio import Redis

from .redis_client import RedisClient
from .redis_config import redis_config


class RedisTokenizer:
    _instance: RedisTokenizer | None = None

    def __new__(cls):
        if cls._instance is None:
            return super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.redis: Redis | None = None
        self._token_cache = TTLCache(maxsize=10000, ttl=300)

    async def get_token(self, user_id: int):
        if self.redis is None:
            self.redis = await RedisClient.get_client()

        if self._token_cache[user_id]:
            return self._token_cache[user_id]

        token = secrets.token_hex(16)
        token_key = f"{redis_config.key_prefix}:anon_token:{token}"

        await self.redis.set(token_key, user_id, ex=60)

        return token

    async def _get_user_id(self, token: str) -> int:
        if self.redis is None:
            self.redis = await RedisClient.get_client()

        token_key = f"{redis_config.key_prefix}:anon_token:{token}"

        user_id = await self.redis.get(token_key)
        return int(user_id) if user_id else None

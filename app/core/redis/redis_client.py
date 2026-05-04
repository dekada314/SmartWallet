import redis.asyncio as aioredis
from redis.asyncio import Redis

from ..logs_config.logger import LogManager
from .redis_config import redis_config


class RedisClient:
    _instance: None | Redis = None
    _app_logger = LogManager().get_logger()

    @classmethod
    async def get_client(cls) -> RedisClient:
        if cls._instance is None:
            redis_url = redis_config.get_url()
            try:
                cls._instance = aioredis.from_url(
                    url=redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_timeout=30,
                    socket_connect_timeout=10,
                    retry_on_timeout=True,
                )
                await cls._instance.ping()
                cls._app_logger.info("[APP] Redis успешно подключен")

            except Exception:
                cls._app_logger.critical("[APP] Не удалось подключить Redis")
                raise

        return cls._instance

    @classmethod
    async def close(cls):
        if cls._instance:
            await cls._instance.close()
            cls._instance = None

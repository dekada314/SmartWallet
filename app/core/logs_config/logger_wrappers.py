import functools

from app.core.logs_config.context import CorrelationContext
from app.core.logs_config.logger import LogManager
from app.core.redis.redis_tokens import RedisTokenizer

_main_logger = LogManager().get_logger("main")
_tokenizer = RedisTokenizer()


def use_case_logger(func):
    @functools.wraps(func)
    async def decorator(*args, **kwargs):
        method_name = func.__name__
        class_name = args[0].__class__.__name__

        _main_logger.debug(
            f"[USE CASE] Начало работы {class_name}.{method_name}", extra={}
        )

        try:
            result = await func(*args, **kwargs)
        except:
            raise

    return decorator


def repository_logger(func):
    @functools.wraps(func)
    async def decorator(*args, **kwargs):
        method_name = func.__name__
        class_name = args[0].__class__.__name__

        _main_logger.debug(
            f"[REPOSITORY] Начало работы {class_name}.{method_name}", extra={}
        )

        try:
            result = await func(*args, **kwargs)
        except:
            raise

    return decorator


def service_logger(func):
    @functools.wraps(func)
    async def decorator(*args, **kwargs):
        method_name = func.__name__
        class_name = args[0].__class__.__name__

        _main_logger.debug(
            f"[SERVICE] Начало работы {class_name}.{method_name}", extra={}
        )

        try:
            result = await func(*args, **kwargs)
        except:
            raise

    return decorator

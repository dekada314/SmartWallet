import functools
from sqlite3 import DatabaseError

from app.core.logs_config.logger import LogManager

_main_logger = LogManager().get_logger("main")
_db_logger = LogManager().get_logger("db")


def use_case_logger(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        method_name = func.__name__
        class_name = args[0].__class__.__name__

        _main_logger.debug(
            f"[USE CASE] Начало работы {class_name}.{method_name}",
        )

        try:
            result = await func(*args, **kwargs)
        except Exception as e:
            _main_logger.exception(
                f"[USE CASE] В работе {class_name}.{method_name} произошла ошибка {e}",
            )
            raise
        else:
            _main_logger.debug(
                f"[USE CASE] {class_name}.{method_name} успешно отработал"
            )
            return result

    return wrapper


def repository_logger(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        method_name = func.__name__
        class_name = args[0].__class__.__name__

        _main_logger.debug(f"[REPOSITORY] Начало работы {class_name}.{method_name}")

        try:
            result = await func(*args, **kwargs)

        except DatabaseError as e:
            _db_logger.error(
                f"[REPOSITORY] Ошибка в работе бд, {class_name}.{method_name}: {e}",
                params=args,
            )
        except Exception as e:
            _main_logger.exception(
                f"[REPOSITORY] В работе {class_name}.{method_name} произошла ошибка {e}",
            )
            raise
        else:
            _main_logger.debug(
                f"[REPOSITORY] {class_name}.{method_name} успешно отработал"
            )
            return result

    return wrapper


def service_logger(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        method_name = func.__name__
        class_name = args[0].__class__.__name__

        _main_logger.debug(f"[SERVICE] Начало работы {class_name}.{method_name}")

        try:
            result = await func(*args, **kwargs)
        except Exception as e:
            _main_logger.exception(
                f"[SERVICE] В работе {class_name}.{method_name} произошла ошибка {e}",
            )
            raise
        else:
            _main_logger.debug(
                f"[SERVICE] {class_name}.{method_name} успешно отработал"
            )
            return result

    return wrapper

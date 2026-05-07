import functools

from app.core.logs_config.logger import LogManager

_main_logger = LogManager().get_logger("main")


def use_case_logger(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        method_name = func.__name__
        class_name = args[0].__class__.__name__

        _main_logger.info(
            f"[USE CASE] Начало работы {class_name}.{method_name}",
        )

        try:
            func(*args, **kwargs)
        except Exception as e:
            _main_logger.exception(
                f"[USE CASE] В работе {class_name}.{method_name} произошка ошибка {e}",
            )
        else:
            _main_logger.info(
                f"[USE CASE] {class_name}.{method_name} успешно отработал"
            )
            raise

    return wrapper


def repository_logger(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        method_name = func.__name__
        class_name = args[0].__class__.__name__

        _main_logger.debug(
            f"[REPOSITORY] Начало работы {class_name}.{method_name}", extra={}
        )

        try:
            await func(*args, **kwargs)
        except Exception as e:
            _main_logger.exception(
                f"[REPOSITORY] В работе {class_name}.{method_name} произошка ошибка {e}",
            )
        else:
            _main_logger.info(
                f"[REPOSITORY] {class_name}.{method_name} успешно отработал"
            )
            raise

    return wrapper


def service_logger(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        method_name = func.__name__
        class_name = args[0].__class__.__name__

        _main_logger.debug(
            f"[SERVICE] Начало работы {class_name}.{method_name}", extra={}
        )

        try:
            await func(*args, **kwargs)
        except Exception as e:
            _main_logger.exception(
                f"[SERVICE] В работе {class_name}.{method_name} произошка ошибка {e}",
            )
        else:
            _main_logger.info(f"[SERVICE] {class_name}.{method_name} успешно отработал")
            raise

    return wrapper

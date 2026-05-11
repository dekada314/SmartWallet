from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import Any

from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, Message, TelegramObject
from pydantic import ValidationError

from app.core.logs_config.context import CorrelationContext
from app.core.logs_config.logger import LogManager
from app.core.redis.redis_tokens import RedisTokenizer


class StatisticsMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self._main_log = LogManager().get_logger("audit")
        self._tg_api_logger = LogManager().get_logger("tg_api")
        self._tokenizer = RedisTokenizer()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ):
        corr_context = CorrelationContext.set()
        start_time = datetime.now()
        duration_time = None
        token = None
        user_id = event.from_user.id
        try:
            token = await self._tokenizer.get_token(user_id=user_id)
            if isinstance(event, Message) and event.text == "Статистика":
                self._main_log.info("[STATS] Вход в блок статистики", user_id=token)
                result = await handler(event, data)
                duration_time = datetime.now() - start_time

            elif isinstance(event, CallbackQuery) and event.data in [
                "per_day",
                "per_week",
                "per_month",
                "per_year",
            ]:
                self._main_log.info(
                    f"[STATS] Обработка запроса {event.data}", user_id=token
                )

                result = await handler(event, data)
                duration_time = datetime.now() - start_time
            else:
                result = await handler(event, data)
                duration_time = datetime.now() - start_time

        except ValidationError:
            self._main_log.error(
                "[STATS] Ошибка валидации параметров статистики", user_id=token
            )

        except TelegramAPIError:
            self._tg_api_logger.error(
                f"[TG_API] Ошибка при обращение к API телеграмма", user_id=token
            )
        except Exception:
            self._main_log.error(f"[STATS] Ошибка работы со статистикой", user_id=token)
            raise
        else:
            self._main_log.info(
                "[STATS] Статисика успешно отображена",
                user_id=token,
                duration_time=duration_time,
            )
            return result
        finally:
            CorrelationContext.reset(corr_context)

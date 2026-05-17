from collections.abc import Awaitable, Callable
from time import perf_counter
from typing import Any

from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramAPIError
from aiogram.types import Message, TelegramObject
from pydantic import ValidationError

from app.core.logs_config.context import CorrelationContext
from app.core.logs_config.logger import LogManager
from app.core.redis.redis_tokens import RedisTokenizer


class GoalMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self._main_log = LogManager().get_logger("main")
        self._tg_api_log = LogManager().get_logger("tg_api")
        self._tokenizer = RedisTokenizer()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> None:
        corr_context = CorrelationContext.set()
        duration_time = None
        start_time = perf_counter()
        try:
            if hasattr(event, "from_user") and event.from_user:
                user_id = event.from_user.id
                token = await self._tokenizer.get_token(user_id=user_id)
            else:
                user_id = "unknown"
                token = "unknown"

            if isinstance(event, Message) and event.text == "Цели":
                self._main_log.info("[GOAL] Вход в рездел целей", user_id=token)

            result = await handler(event, data)
            duration_time = perf_counter() - start_time

            self._main_log.info(
                "[GOAL] Обработка целей закончена успешно",
                user_id=token,
                duration_time=duration_time,
            )
            return result

        except ValidationError:
            self._main_log.error(
                "[GOAL] Ошибка валидации параметров цели", user_id=token
            )

        except TelegramAPIError:
            self._tg_api_log.error(
                f"[TG_API] Ошибка при обращении к API телеграмма", user_id=token
            )
        except Exception:
            self._main_log.error(f"[GOAL] Ошибка обработки целей", user_id=token)
            raise
        finally:
            CorrelationContext.reset(corr_context)

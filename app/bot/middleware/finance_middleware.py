from collections.abc import Awaitable, Callable
from time import perf_counter
from typing import Any

from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, TelegramObject
from pydantic import ValidationError

from app.core.logs_config.context import CorrelationContext
from app.core.logs_config.logger import LogManager
from app.core.redis.redis_tokens import RedisTokenizer


class FinanceMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self._audit_logger = LogManager().get_logger("audit")
        self._tg_api_logger = LogManager().get_logger("tg_api")
        self._tokenizer = RedisTokenizer()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ):
        corr_context = CorrelationContext.set()
        start_time = perf_counter()
        duration_time = None
        amount = None
        operation_type = None
        try:
            if hasattr(event, "from_user") and event.from_user:
                user_id = event.from_user.id
                token = await self._tokenizer.get_token(user_id=user_id)
            else:
                user_id = "unknown"
                token = "unknown"

            if isinstance(event, Message) and event.text in [
                "Ввести доход",
                "Ввести расход",
            ]:
                self._audit_logger.info(
                    "[AUDIT] Вход в блок транзакций",
                    user_id=token,
                )

            state: FSMContext = data.get("state")
            if state:
                current_state = await state.get_state()
                if current_state and current_state.startswith(
                    ("IncomeForm", "ExpenseForm")
                ):
                    self._audit_logger.info(
                        "[AUDIT] Начало обработки транзакции", user_id=token
                    )

            result = await handler(event, data)
            duration_time = perf_counter() - start_time

            if result:
                operation_type, amount = result

                self._audit_logger.info(
                    "[AUDIT] Транзакция успешно обработана",
                    user_id=token,
                    amount=amount,
                    operation_type=operation_type,
                    duration_time=duration_time,
                )
            return result

        except ValidationError:
            self._audit_logger.error(
                "[AUDIT] Ошибка валидации параметров транзакции", user_id=token
            )
            raise

        except TelegramAPIError:
            self._tg_api_logger.error(
                f"[TG_API] Ошибка при обращение к API телеграмма", user_id=token
            )
            raise
        except Exception:
            self._audit_logger.error(
                f"[AUDIT] Ошибка обработки транзакции", user_id=token
            )
            raise
        finally:
            CorrelationContext.reset(corr_context)

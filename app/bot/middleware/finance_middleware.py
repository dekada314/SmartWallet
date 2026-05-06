from collections.abc import Awaitable, Callable
from datetime import datetime
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
        start_time = datetime.now()
        duration_time = None
        token = None
        amount = None
        operation_type = None
        try:
            user_id = event.from_user.id
            token = await self._tokenizer.get_token(user_id=user_id)
            if isinstance(event, Message) and event.text in [
                "Ввести доход",
                "Ввести расход",
            ]:
                self._audit_logger.info(
                    "[AUDIT] Вход в блок транзакций",
                    extra={
                        "user_id": token,
                    },
                )

            raw_state = data.get("raw_state")
            if raw_state and raw_state.startswith(("IncomeForm", "ExpenseForm")):
                self._audit_logger.info(
                    "[AUDIT] Начало обработки транзакции",
                    extra={"user_id": token},
                )
            result = await handler(event, data)
            duration_time = datetime.now() - start_time

        except ValidationError:
            self._audit_logger.error(
                "[AUDIT] Ошибка валидации параметров транзакции",
                extra={
                    "user_id": token,
                },
            )

        except TelegramAPIError:
            self._tg_api_logger.error(
                f"[TG_API] Ошибка при обращение к API телеграмма",
                extra={"user_id": token},
            )
        except Exception:
            self._audit_logger.error(
                f"[AUDIT] Ошибка обработки транзакции",
                extra={
                    "user_id": token,
                },
            )
            raise

        else:
            state: FSMContext = data.get("state")
            if state:
                state_data = await state.get_data()
                amount = state_data.get("amount", None)
                operation_type = state_data.get("operation_type", None)

            self._audit_logger.info(
                "[AUDIT] Транзакция успешно обработана",
                extra={
                    "user_id": token,
                    "amount": amount if amount else None,
                    "operation_type": operation_type if operation_type else None,
                    "duration_time": duration_time if duration_time else None,
                },
            )
            return result
        finally:
            CorrelationContext.reset(corr_context)

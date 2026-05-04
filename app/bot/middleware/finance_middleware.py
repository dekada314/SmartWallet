from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import Any

from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, TelegramObject
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
        start_time = datetime.now()
        user_id = event.from_user.id
        token = await self._tokenizer.get_token(user_id=user_id)
        try:
            if event.text in ["Ввести доход", "Ввести расход"]:
                CorrelationContext.set()
                self._audit_logger.info(
                    "[AUDIT] Вход в блок транзакций",
                    extra={
                        "user_id": token,
                    },
                )

            current_state: FSMContext = data.get("state", None)
            if current_state and str(current_state).startswith(
                ("IncomeForm", "ExpenseForm")
            ):
                self._audit_logger.info(
                    "[AUDIT] Начало обработки транзакции",
                    extra={"user_id": token},
                )

                await handler(event, data)
                duration_time = datetime.now() - start_time
            else:
                await handler(event, data)

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

        else:
            state: FSMContext = data.get("state")
            if state:
                state_data = await state.get_data()
                amount = state_data["amount"]
                operation_type = state_data["operation_type"]

            self._audit_logger.info(
                "[AUDIT] Транзакция успешно обработана",
                extra={
                    "user_id": token,
                    "amount": amount,
                    "operation_type": operation_type,
                    "duration_time": duration_time,
                },
            )
        finally:
            CorrelationContext.reset()

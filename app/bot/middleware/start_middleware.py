from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramAPIError
from pydantic import ValidationError

from app.core.logs_config.context import CorrelationContext
from app.core.logs_config.logger import LogManager
from app.core.redis.redis_tokens import RedisTokenizer


class StartMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self._registry_log = LogManager().get_logger("main")
        self._tg_api_log = LogManager().get_logger("tg_api")
        self._tokenizer = RedisTokenizer()

    async def __call__(self, handler, event, data):
        corr_context = CorrelationContext.set()
        token = None
        try:
            user_id = event.from_user.id
            token = await self._tokenizer.get_token(user_id=user_id)
            result = await handler(event, data)

            if result:
                self._registry_log.info(
                    "[REGISTRY] Пользователь успешно зарегистрирован",
                    extra={"user_token": token},
                )

            else:
                self._registry_log.info(
                    "[REGISTRY] Попытка повторной регистрации пользователя",
                    extra={"user_token": token},
                )
            return result
        except ValidationError:
            self._registry_log.error(
                "[REGISTRY] Ошибка регистрации пользователя",
                extra={"user_token": token},
            )

        except TelegramAPIError:
            self._tg_api_log.error(
                f"[TG_API] Ошибка при обращение к API телеграмма",
                extra={"user_id": token},
            )

        except Exception:
            self._registry_log.error(
                f"[REGISTRY] Ошибка обработки цели",
                extra={
                    "user_id": token,
                },
            )
            raise

        finally:
            CorrelationContext.reset(corr_context)

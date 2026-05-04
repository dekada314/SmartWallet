import uuid
from contextvars import ContextVar, Token


class CorrelationContext:
    _correlation_id: ContextVar | None = ContextVar("correlation_id", default=None)

    @classmethod
    def get(cls) -> str | None:
        return cls._correlation_id.get()

    @classmethod
    def set(cls) -> Token:
        corr_id = str(uuid.uuid4)
        return cls._correlation_id.set(corr_id)

    @classmethod
    def reset(cls, token) -> None:
        cls._correlation_id.reset(token)

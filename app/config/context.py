import uuid
from contextvars import ContextVar

correlation_id = ContextVar(
    "correlation_id",
    default=""
)


def set_corellation_id():
    cid = str(uuid.uuid4)
    correlation_id.set(cid)
    return cid


def get_correlation_id():
    return correlation_id.get()
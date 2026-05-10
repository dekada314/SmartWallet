from dataclasses import dataclass, field
from datetime import datetime

from domain.enums.transaction_type import TransactionType


@dataclass(slots=True)
class Transaction:
    user_id: int
    order_number: int
    category: str
    amount: float
    source_text: str | None
    transaction_type: TransactionType
    created_at: datetime = field(default_factory=datetime.now)
    id: int | None = None

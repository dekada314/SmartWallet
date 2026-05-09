from dataclasses import dataclass, field
from datetime import date, datetime

from domain.enums.transaction_type import TransactionType


@dataclass(slots=True)
class Transaction:
    id: int
    user_id: int
    user_transaction_id: int
    category: str
    amount: float
    source_text: str | None
    transaction_type: TransactionType
    created_at: date = field(default_factory=datetime.now)

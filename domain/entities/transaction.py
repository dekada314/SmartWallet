from dataclasses import dataclass
from datetime import date, datetime

from domain.enums.transaction_type import TransactionType


@dataclass(slots=True)
class Transaction:
    user_id: int
    user_transaction_id: int
    category: str
    amount: float
    source_text: str | None
    transaction_type: TransactionType
    created_at: date = datetime.now()

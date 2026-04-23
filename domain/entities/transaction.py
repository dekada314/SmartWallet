from dataclasses import dataclass
from datetime import date, datetime

from domain.enums import TransactionType


@dataclass(slots=True)
class Transaction:
    user_id: int
    user_transaction_id: int
    category: str
    amount: float
    transaction_type: TransactionType
    source_text: str
    created_at: None | date = datetime.now()

    def __post_init__(self):
        if str(self.amount) not in self.source_text:
            raise ValueError

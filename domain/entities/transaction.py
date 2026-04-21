from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID, uuid4


@dataclass(slots=True)
class Transaction:
    user_id: int
    user_transaction_id: int
    category: str
    amount: float
    created_at: date = datetime.now()

    def __post_init__(self):
        if not isinstance(self.category, str):
            raise ValueError

        if self.amount < 0:
            raise ValueError

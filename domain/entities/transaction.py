from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID, uuid4


@dataclass(slots=True)
class Transaction:
    category: str
    amount: float
    created_at: date = datetime.now()
    transaction_id: str = str(uuid4())

    def __post_init__(self):
        if not isinstance(self.category, str):
            raise ValueError

        if self.amount < 0:
            raise ValueError

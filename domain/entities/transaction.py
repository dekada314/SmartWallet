from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID


@dataclass(slots=True, frozen=True)
class Transaction:
    transaction_id: UUID
    category: str
    amount: float
    created_at: date = datetime.now()
    description: str = ''
    
    def __post_init__(self):
        pass
from dataclasses import dataclass
from datetime import date, datetime


@dataclass(slots=True, frozen=True)
class User:
    user_id: str
    user_name: str
    balance: float
    created_at: date = datetime.now()

    def __post_init__(self):
        if self.user_id < 0:
            raise ValueError()

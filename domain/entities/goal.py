from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class Goal:
    id: int
    user_id: int
    order_number: int
    target: float
    curr_bill: float
    text: str
    created_at: datetime = field(default_factory=datetime.now())

    def __post_init__(self):
        if self.user_id < 0:
            raise ValueError("Значение user_id не может быть отрицательным")
        if self.target < 0 or self.curr_bill < 0:
            raise ValueError("Значение вклада не может быть отрицательным")

    def add_amount(self, value) -> None:
        self.curr_bill += value
        if self.is_achieved():
            return self.curr_bill - self.target
        return None

    def is_achieved(self) -> bool:
        return self.curr_bill >= self.target

    def get_progress(self) -> str:
        return f"{self.curr_bill / self.target:.1}%"

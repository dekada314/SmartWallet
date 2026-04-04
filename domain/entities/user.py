from dataclasses import dataclass
from datetime import date, datetime


@dataclass(slots=True)
class User:
    user_id: str
    user_name: str
    balance: float
    created_at: date
    last_action: date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __post_init__(self):
        if self.user_id < 0:
            raise ValueError

    def change_user_name(self, new_name: str):
        if isinstance(new_name, str):
            self.user_name = new_name

    def add_amount(self, value: int | float):
        if isinstance(value, (int, float)):
            if 0 < value < 1_000_000:
                self.balance += value
            else:
                raise ValueError("Недопустимое численное значение!")

    def update_last_action(self) -> None:
        self.last_action = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

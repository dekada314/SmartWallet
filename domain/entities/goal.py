from dataclasses import dataclass


@dataclass(slots=True)
class Goal:
    user_id: int
    user_goal_id: int
    target: float
    curr_bill: float
    text: str

    def __post_init__(self):
        if self.user_id < 0:
            raise ValueError("Значение user_id не может быть отрицательным")
        if self.target < 0 or self.curr_bill < 0:
            raise ValueError("Значение вклада не может быть отрицательным")

    def add_amount(self, value):
        self.curr_bill += value
        if self.is_achieved():
            return self.curr_bill - self.target
        return None

    def is_achieved(self):
        return self.curr_bill >= self.target

    def get_progress(self):
        return f"{self.curr_bill / self.target:.1}%"

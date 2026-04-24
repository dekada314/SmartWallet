from pydantic import BaseModel, field_validator

from use_cases.exceptions import NotValidAmountError


class SaveIncomeRequest(BaseModel):
    user_id: int
    amount: float

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount(cls, field_value: str):
        parsed_amount = field_value.replace(",", ".").strip("$ ")
        if not parsed_amount:
            raise ValueError("Неверное значение суммы")
        return parsed_amount

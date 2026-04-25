from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class SaveGoalRequest(BaseModel):
    user_id: int = Field(gt=0)
    amount: float
    text: str

    @field_validator("amount", mode="before")
    @classmethod
    def amount_must_be_number(cls, field_value: str) -> str:
        if isinstance(field_value, str):
            field_value = field_value.strip().replace(",", ".")
        return field_value

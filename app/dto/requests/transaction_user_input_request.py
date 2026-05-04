from pydantic import BaseModel, Field, field_validator


class SaveTransactionRequest(BaseModel):
    user_id: int = Field(gt=0)
    category: str
    amount: float

    @field_validator("category")
    @classmethod
    def transaction_text_must_be_not_empty(cls, field_value: str) -> str:
        if not field_value.strip():
            raise ValueError("Текст транзакции должен быть не пустым")
        return field_value

    @field_validator("amount", mode="before")
    @classmethod
    def amount_must_be_number(cls, field_value: str) -> str:
        if isinstance(field_value, str):
            field_value = field_value.strip().replace(",", ".")
        return field_value

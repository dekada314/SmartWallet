from pydantic import BaseModel, Field, field_validator


class TransactionTextInputRequest(BaseModel):
    user_id: int = Field(gt=0)
    text: str

    @field_validator("text")
    @classmethod
    def transaction_text_must_not_be_empty(cls, field_value: str) -> str:
        if not field_value.strip():
            raise ValueError("Текст транзакции должен быть не пустым")
        if not any(ch.isdigit() for ch in field_value):
            raise ValueError("Текст должен содержать хотя бы одну цифру")
        return field_value

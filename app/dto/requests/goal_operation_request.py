from pydantic import BaseModel, Field, field_validator


class GoalOperationRequest(BaseModel):
    owner_id: int = Field(gt=0)
    text: str

    @field_validator("text")
    @classmethod
    def transaction_text_must_not_be_empty(cls, field_value: str) -> str:
        if not field_value.strip():
            raise ValueError("Текст транзакции должен быть не пустым")
        return field_value

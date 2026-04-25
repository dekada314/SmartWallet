from pydantic import BaseModel, Field, field_validator


class UserRegistryRequest(BaseModel):
    user_id: int = Field(gt=0)
    user_name: str

    @field_validator("user_name")
    @classmethod
    def user_name_must_not_be_empty(cls, field_value: str) -> str:
        if not field_value.strip():
            raise ValueError("Имя не должно быть пустым")
        return field_value

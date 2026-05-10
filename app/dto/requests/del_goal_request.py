from pydantic import BaseModel, Field, field_validator


class DelGoalRequest(BaseModel):
    user_id: int = Field(gt=0)
    order_number: int = Field(gt=0)

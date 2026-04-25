from decimal import Decimal

from pydantic import BaseModel, field_validator


class StatisticsResponse(BaseModel):
    income_balance: float
    income_count: int
    expense_balance: float
    expense_count: int

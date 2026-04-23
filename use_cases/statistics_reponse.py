from decimal import Decimal

from pydantic import BaseModel, field_validator


class StatisticsResponse(BaseModel):
    income_balance: Decimal
    income_count: int
    expense_balance: Decimal
    expense_count: int

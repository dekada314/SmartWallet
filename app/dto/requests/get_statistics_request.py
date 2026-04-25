from pydantic import BaseModel, Field, field_validator

from application.use_cases.enums import PeriodType


class StatisticsRequest(BaseModel):
    user_id: int = Field(gt=0)
    period: PeriodType

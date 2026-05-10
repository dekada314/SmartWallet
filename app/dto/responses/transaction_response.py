from pydantic import BaseModel, Field

from domain.entities.transaction import Transaction


class TransactionReponse(BaseModel):
    transaction: Transaction
    warnings: list[str] | None = Field(default_factory=list)

from datetime import date, datetime
from uuid import UUID, uuid4

from domain.entities.transaction import Transaction
from repository.base_transaction_repository import BaseTransactionRepository


class AddExpenseUseCase:
    def __init__(self, transaction_repository: BaseTransactionRepository):
        self.transaction_repositry = transaction_repository
        
    async def execute(self, transaction_id: UUID, amount: float) -> Transaction:
        tranaction = self.transaction_repositry.find_transaction_by_id(transaction_id)
        
        if tranaction:
            return tranaction
        
        new_transaction = Transaction(
            transaction_id,
            datetime.now(),
            category=None,
            amount = amount
        )
        
        self.transaction_repositry.save_transaction(new_transaction)
        
        return new_transaction
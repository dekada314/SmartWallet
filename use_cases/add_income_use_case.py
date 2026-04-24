from app.requests.save_income_request import SaveIncomeRequest
from domain.entities.transaction import Transaction
from domain.entities.user import User
from domain.enums import TransactionType
from repository.base_user_repository import BaseUserRepository
from repository.base_transaction_repository import BaseTransactionRepository

from .exceptions import GettingUserError


class AddIncomeUseCase:
    def __init__(
        self,
        user_repository: BaseUserRepository,
        transaction_repository: BaseTransactionRepository
    ):
        self.user_repository = user_repository
        self.transction_repository = transaction_repository

    async def execute(self, income_dto: SaveIncomeRequest) -> None | float:
        user: User = await self.user_repository.get_user_by_user_id(income_dto.user_id)

        if not user:
            raise GettingUserError
        
        last_user_id: int = await self.transction_repository.get_last_id(income_dto.user_id)
        
        new_income_transaction = Transaction(
            user_id=income_dto.user_id,
            user_transaction_id=last_user_id + 1,
            category=None,
            amount=income_dto.amount,
            source_text=None,
            transaction_type=TransactionType.INCOME
        )

        user.add_amount(income_dto.amount)
        user.update_last_action()
        
        await self.user_repository.save_user(user)
        await self.transction_repository.save_transaction(new_income_transaction)
    
        return user.balance

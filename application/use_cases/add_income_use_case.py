from app.core.logs_config.logger_wrappers import use_case_logger
from app.dto.requests.save_income_request import SaveIncomeRequest
from domain.entities.transaction import Transaction
from domain.entities.user import User
from domain.enums.transaction_type import TransactionType
from domain.repositories.base_transaction_repository import BaseTransactionRepository
from domain.repositories.base_user_repository import BaseUserRepository

from ..exceptions.exceptions import GettingUserError


class AddIncomeUseCase:
    def __init__(
        self,
        user_repository: BaseUserRepository,
        transaction_repository: BaseTransactionRepository,
    ):
        self.user_repository = user_repository
        self.transction_repository = transaction_repository

    @use_case_logger
    async def execute(self, income_dto: SaveIncomeRequest) -> None | float:
        user: User = await self.user_repository.get_user_by_user_id(income_dto.user_id)

        if not user:
            raise GettingUserError

        last_user_id: int = await self.transction_repository.get_last_id(
            income_dto.user_id
        )

        transaction = Transaction(
            user_id=income_dto.user_id,
            order_number=last_user_id + 1,
            category=None,
            amount=income_dto.amount,
            source_text=None,
            transaction_type=TransactionType.INCOME.value,
        )

        user.add_amount(income_dto.amount)
        await self.user_repository.update_balance(user.user_id, transaction.amount)
        await self.user_repository.update_last_action(user.user_id)

        await self.transction_repository.save_transaction(transaction)

        return user.balance

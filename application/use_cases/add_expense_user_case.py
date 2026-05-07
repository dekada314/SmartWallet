from app.core.logs_config.logger_wrappers import use_case_logger
from app.dto.requests.save_transaction_request import SaveTransactionRequest
from application.exceptions.exceptions import GettingUserError
from domain.entities.transaction import Transaction
from domain.entities.user import User
from domain.enums.transaction_type import TransactionType
from domain.repositories.base_categories_repository import BaseCategoriesRepositry
from domain.repositories.base_transaction_repository import BaseTransactionRepository
from domain.repositories.base_user_repository import BaseUserRepository
from infrastructure.ml.embeddings.text_processing import TextProcessing


class AddExpenseUseCase:
    def __init__(
        self,
        transaction_repository: BaseTransactionRepository,
        categories_repository: BaseCategoriesRepositry,
        user_repository: BaseUserRepository,
        text_processing_unit: TextProcessing,
    ):
        self.transaction_repositry = transaction_repository
        self.categories_repository = categories_repository
        self.user_repository = user_repository
        self.text_processing = text_processing_unit

    @use_case_logger
    async def execute(self, dto: SaveTransactionRequest) -> Transaction | None:
        user: User = await self.user_repository.get_user_by_user_id(dto.user_id)

        if not user:
            raise GettingUserError

        if dto.category is not None:
            output_category = dto.category
            amount = float(dto.text)
            source_text = None
        else:
            amount: float = self.text_processing.extract_amount(dto.text)
            cat, _ = self.text_processing.classifier(dto.text)
            output_category = cat
            source_text = dto.text

        last_user_id = await self.transaction_repositry.get_last_id(dto.user_id)

        new_transaction = Transaction(
            user_id=dto.user_id,
            user_transaction_id=last_user_id + 1,
            category=output_category,
            amount=amount,
            source_text=source_text,
            transaction_type=TransactionType.EXPENSE,
        )
        try:
            await self.transaction_repositry.save_transaction(new_transaction)
            await self.user_repository.update_balance(
                new_transaction.user_id, -new_transaction.amount
            )
            await self.user_repository.update_last_action(new_transaction.user_id)
        except:
            raise

        return new_transaction

from datetime import datetime, time

from app.core.logs_config.logger_wrappers import use_case_logger
from app.dto.requests.save_transaction_request import SaveTransactionRequest
from app.dto.responses.transaction_response import TransactionReponse
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
    async def execute(
        self, dto: SaveTransactionRequest
    ) -> tuple[Transaction, list[str]] | None:
        user: User = await self.user_repository.get_user_by_user_id(dto.user_id)
        if not user:
            raise GettingUserError

        if dto.category is not None:
            output_category = dto.category
            amount = float(dto.text)
            source_text = None
        else:
            amount: float = self.text_processing.extract_amount(dto.text)
            cat, _ = await self.text_processing.classifier(dto.text)
            output_category = cat
            source_text = dto.text

        last_user_id = await self.transaction_repositry.get_last_id(dto.user_id)

        transaction = Transaction(
            user_id=dto.user_id,
            order_number=last_user_id + 1,
            category=output_category,
            amount=amount,
            source_text=source_text,
            transaction_type=TransactionType.EXPENSE.value,
        )

        rules = self.categories_repository.get_categories_rules(transaction.category)
        hints_for_user = []
        if rules:
            context = {
                "transaction": transaction,
                "user": user,
                "day_of_week": datetime.now().weekday(),
                "current_time": datetime.now().time(),
                "limit_time": time(23, 0),
                "category_limit": self.categories_repository.get_waste_for_cat(
                    transaction.category
                ),
            }

            for rule in rules:
                condition = rule.get("condition", "")
                if condition:
                    try:
                        if eval(condition, {"__builtins__": {}}, context):
                            hints_for_user.append(
                                rule.get("text", "Даже и посоветовать нечего)")
                            )
                    except Exception:
                        pass
        try:
            await self.transaction_repositry.save_transaction(transaction)
            await self.user_repository.update_balance(
                transaction.user_id, -transaction.amount
            )
            await self.user_repository.update_last_action(transaction.user_id)
        except:
            raise
        transaction.category = self.categories_repository.get_category_name_by_id(
            transaction.category
        )
        return TransactionReponse(transaction=transaction, warnings=hints_for_user)

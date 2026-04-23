from datetime import date, datetime
from uuid import UUID, uuid4

from domain.entities.transaction import Transaction
from domain.entities.user import User
from handlers.requests.save_transaction_request import SaveTransactionRequest
from model.basic_classifier import BasicClassifier
from repository.base_categories_repository import BaseCategoriesRepositry
from repository.base_transaction_repository import BaseTransactionRepository
from repository.base_user_repository import BaseUserRepository
from services.text_processing import TextProcessing


class AddExpenseUseCase:
    def __init__(
        self,
        transaction_repository: BaseTransactionRepository,
        categories_repository: BaseCategoriesRepositry,
        user_repository: BaseUserRepository,
        classifier: BasicClassifier,
    ):
        self.transaction_repositry = transaction_repository
        self.categories_repository = categories_repository
        self.user_repository = user_repository
        self.model = classifier

    async def execute(
        self, dto: SaveTransactionRequest, category: str = None
    ) -> Transaction | None:
        if not dto.owner_id or not dto.text:
            raise ValueError

        cat_examples = self.categories_repository.get_categiries_examples()

        self.text_processing = TextProcessing(cat_examples=cat_examples)

        if category is not None:
            output_category = category
            amount = float(dto.text)
        else:
            amount: float = self.text_processing.extract_amount(dto.text)
            cat, conf = self.text_processing.classifier(dto.text)
            if conf > 0.7:
                output_category = cat

        new_transaction = Transaction(
            user_id=dto.owner_id,
            user_transaction_id=self.transaction_repositry.get_last_id(dto.owner_id)
            + 1,
            category=output_category,
            amount=amount,
        )

        await self.transaction_repositry.save_transaction(new_transaction)
        await self.user_repository.update_balance(
            new_transaction.user_id, -new_transaction.amount
        )
        await self.user_repository.update_last_action(new_transaction.user_id)

        return new_transaction

from app.dto.requests.save_transaction_request import SaveTransactionRequest
from domain.entities.transaction import Transaction
from domain.enums.transaction_type import TransactionType
from domain.repositories.base_categories_repository import BaseCategoriesRepositry
from domain.repositories.base_transaction_repository import BaseTransactionRepository
from domain.repositories.base_user_repository import BaseUserRepository
from infrastructure.ml.classifier.basic_classifier import BasicClassifier
from infrastructure.ml.embeddings.text_processing import TextProcessing


class AddExpenseUseCase:
    def __init__(
        self,
        transaction_repository: BaseTransactionRepository,
        categories_repository: BaseCategoriesRepositry,
        user_repository: BaseUserRepository,
        text_processing_unit: TextProcessing,
        classifier: BasicClassifier,
    ):
        self.transaction_repositry = transaction_repository
        self.categories_repository = categories_repository
        self.user_repository = user_repository
        self.text_processing = text_processing_unit
        self.model = classifier

    async def execute(
        self, dto: SaveTransactionRequest, category: str = None
    ) -> Transaction | None:
        if category is not None:
            output_category = category
            amount = float(dto.text)
            source_text = None
        else:
            amount: float = self.text_processing.extract_amount(dto.text)
            cat, conf = self.text_processing.classifier(dto.text)
            # if conf > 0.7:
            output_category = cat
            source_text = dto.text

        last_user_id = await self.transaction_repositry.get_last_id(dto.owner_id)

        new_transaction = Transaction(
            user_id=dto.owner_id,
            user_transaction_id=last_user_id + 1,
            category=output_category,
            amount=amount,
            source_text=source_text,
            transaction_type=TransactionType.EXPENSE,
        )

        await self.transaction_repositry.save_transaction(new_transaction)
        await self.user_repository.update_balance(
            new_transaction.user_id, -new_transaction.amount
        )
        await self.user_repository.update_last_action(new_transaction.user_id)

        return new_transaction

from datetime import date, datetime
from uuid import UUID, uuid4

from domain.entities.transaction import Transaction
from model.basic_classifier import BasicClassifier
from repository.base_categories_repository import BaseCategoriesRepositry
from repository.base_transaction_repository import BaseTransactionRepository
from services.text_processing import TextProcessing


class AddExpenseUseCase:
    def __init__(
        self,
        transaction_repository: BaseTransactionRepository,
        categories_repository: BaseCategoriesRepositry,
        classifier: BasicClassifier,
    ):
        self.transaction_repositry = transaction_repository
        self.categories_repository = categories_repository
        self.text_processing = TextProcessing()
        self.model = classifier

    async def execute(self, user_id: int, text: str) -> Transaction | None:
        if not user_id or not text:
            raise ValueError
        
        amount = self.text_processing.number_searcher(text)
        main_lemma = self.text_processing.main_noun_searcher(text)[0]
        
        if not amount or not main_lemma:
            raise ValueError 

        output_category = self.categories_repository.keyword_search(main_lemma)

        if not output_category:
            output_category, prob = self.model.predict(main_lemma)

        new_transaction = Transaction(
            category=output_category,
            amount=amount,
        )

        await self.transaction_repositry.save_transaction(user_id, new_transaction)

        return new_transaction

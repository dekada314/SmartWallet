from abc import ABC, abstractmethod
from datetime import datetime

from domain.entities.transaction import Transaction


class BaseTransactionRepository(ABC):
    @abstractmethod
    async def get_last_id(self, user_id: int) -> int: ...

    @abstractmethod
    async def save_transaction(self, transaction: Transaction) -> None: ...

    @abstractmethod
    async def delete_by_transaction_id(
        self, user_id: int, order_number: int
    ) -> int: ...

    @abstractmethod
    async def get_transaction_by_transaction_id(
        self, user_id: int, order_number: int
    ) -> Transaction | None: ...

    @abstractmethod
    async def get_user_transactions_count(self, user_id: int) -> int: ...

    @abstractmethod
    async def get_transactions_by_period(
        self, user_id: int, start_time: datetime, end_date: datetime
    ) -> int: ...

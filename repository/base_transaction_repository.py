from abc import ABC, abstractmethod

from domain.entities.transaction import Transaction


class BaseTransactionRepository(ABC):
    @abstractmethod
    async def save_transaction() -> None: ...

    # @abstractmethod
    # async def delete_transaction() -> None: ...

    # @abstractmethod
    # async def get_users_tr_for_day() -> list[Transaction]: ...

    # @abstractmethod
    # async def find_transaction_by_date() -> None: ...

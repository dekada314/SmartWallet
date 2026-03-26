from abc import ABC, abstractmethod

from domain.entities.user import User


class BaseUserRepository(ABC):
    @abstractmethod
    async def save_user() -> None: ...

    @abstractmethod
    async def delete_user_by_user_id() -> None: ...

    @abstractmethod
    async def get_user_by_user_id() -> User | None: ...

    @abstractmethod
    async def update_last_action() -> None: ...
    @abstractmethod
    async def update_balance() -> None: ...

    # @abstractmethod
    # async def get_user_by_id() -> User | None: ...

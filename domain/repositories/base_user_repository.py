from abc import ABC, abstractmethod

from domain.entities.user import User


class BaseUserRepository(ABC):
    @abstractmethod
    async def save_user(self, user: User) -> None: ...

    @abstractmethod
    async def delete_user_by_user_id(self, user_id: int) -> None: ...

    @abstractmethod
    async def get_user_by_user_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    async def update_last_action(self, user_id: int) -> None: ...

    @abstractmethod
    async def update_balance(self, user_id: int, delta: int | float) -> None: ...

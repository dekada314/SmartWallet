from abc import ABC, abstractmethod


class BaseCategoriesRepositry(ABC):
    @abstractmethod
    async def get_all_categories() -> dict: ...

    @abstractmethod
    async def get_categiries_examples() -> str | None: ...

    # @abstractmethod
    # async def get_list_categories() -> list[str]:
    #     ...

    # @abstractmethod
    # async def delete_repository() -> None:
    #     ...

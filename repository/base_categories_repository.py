from abc import ABC, abstractmethod


class BaseCategoriesRepositry(ABC):
    @abstractmethod
    async def get_all_categories() -> dict: ...

    @abstractmethod
    async def save_category() -> None: ...

    @abstractmethod
    async def keyword_search() -> str | None: ...

    # @abstractmethod
    # async def get_list_categories() -> list[str]:
    #     ...

    # @abstractmethod
    # async def delete_repository() -> None:
    #     ...

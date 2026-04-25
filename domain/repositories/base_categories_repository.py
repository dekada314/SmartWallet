from abc import ABC, abstractmethod


class BaseCategoriesRepositry(ABC):
    @abstractmethod
    async def get_all_categories() -> dict: ...

    @abstractmethod
    async def get_all_categories_examples() -> dict[str : list[int]]: ...

    # @abstractmethod
    # async def get_list_categories() -> list[str]:
    #     ...

    # @abstractmethod
    # async def delete_repository() -> None:
    #     ...

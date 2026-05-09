from abc import ABC, abstractmethod


class BaseCategoriesRepositry(ABC):
    @abstractmethod
    def get_all_categories(self) -> list: ...

    @abstractmethod
    def get_all_categories_examples(self) -> dict[str, list[str]]: ...

    @abstractmethod
    def get_categories_rules(self, cat_name: str) -> dict[str, list[str, str, str]]: ...

    @abstractmethod
    def get_waste_for_cat(self, cat_name: str) -> int: ...
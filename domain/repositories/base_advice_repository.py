from abc import ABC, abstractmethod


class BaseAdviceRepository:
    @abstractmethod
    def get_all_advices(self) -> None: ...

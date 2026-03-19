from abc import ABC, abstractmethod


class BasicClassifier(ABC):
    @abstractmethod
    async def predict(self, word: str) -> tuple[str, float]: ...

    @abstractmethod
    async def retrain(self) -> None: ...

from abc import ABC, abstractmethod


class BasicClassifier(ABC):
    @abstractmethod
    async def predict(self, word: str) -> tuple[str, float]:
        """
        Получает одно слово: лемму существительного
        Возвращает кортеж вида (категория, вероятность этой категории)
        """

    @abstractmethod
    async def retrain(self) -> None:
        """
        Дообучение на обновленном датасете
        """

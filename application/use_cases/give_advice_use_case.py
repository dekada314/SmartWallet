import random

import yaml

from app.dto.responses.advice_reponse import AdviceModel
from domain.repositories.base_advice_repository import BaseAdviceRepository


class GiveAdviceUseCase:
    def __init__(self, advices_repo: BaseAdviceRepository):
        self.advices_repo = advices_repo

    async def execute(self) -> str:
        advices = self.advices_repo.get_all_advices()

        advice: dict[str, str] = list(random.choice(advices).values())[0]
        return AdviceModel(name=advice["name"], desc=advice["description"])

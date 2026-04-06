import random

import yaml


class GiveAdviceUseCase:
    def __init__(self, advices_path: str):
        self.advices_path = advices_path

    def execute(self) -> str:
        with open(self.advices_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
        advices = data["types"]
        item = random.choice(advices)
        key = list(item.keys())[0]
        advice = item[key]
        return f"{advice['name']}\n\n{advice['description']}"

from pathlib import Path

import yaml

import app.config.settings as settings
from domain.repositories.base_advice_repository import BaseAdviceRepository


class YamlAdvicesRepository(BaseAdviceRepository):
    def __init__(self, knowledge_base_path: Path):
        self.kb = knowledge_base_path / "advices.yml"

    def get_all_advices(self):
        with open(self.kb, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)["types"]

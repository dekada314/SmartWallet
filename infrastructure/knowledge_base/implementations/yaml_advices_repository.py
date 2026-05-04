import yaml

import app.config.settings as settings
from domain.repositories.base_advice_repository import BaseAdviceRepository


class YamlAdvicesRepository(BaseAdviceRepository):
    def __init__(self, advice_kb_path: str):
        self.kb = advice_kb_path

    def get_all_advices(self):
        with open(self.kb, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)["types"]

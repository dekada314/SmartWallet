import yaml
from repository.base_categories_repository import BaseCategoriesRepositry

import app.config.settings as settings


class YamlCategoriesRepository(BaseCategoriesRepositry):
    def __init__(self, kb_path: str):
        self.kb = kb_path

    def get_all_categories(self) -> dict:
        with open(self.kb, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)["ontology"]["categories"]

    def get_all_categories_examples(self) -> dict[str : list[str]]:
        with open(self.kb, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)["category_examples"]

    def get_categiries_examples(self):
        with open(self.kb, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)["category_examples"]

    def get_lexicon(self):
        with open(self.kb, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)["lexicon"]

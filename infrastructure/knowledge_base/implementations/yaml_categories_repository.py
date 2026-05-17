from pathlib import Path

import yaml

from domain.repositories.base_categories_repository import BaseCategoriesRepositry


class YamlCategoriesRepository(BaseCategoriesRepositry):
    def __init__(self, knowledge_base_path: Path):
        self.kb = knowledge_base_path

    def get_all_categories(self) -> list:
        with open(self.kb / "ontology.yml", "r", encoding="utf-8") as file:
            return yaml.safe_load(file)["ontology"]["categories"]

    def get_category_name_by_id(self, category_name):
        with open(self.kb / "ontology.yml", "r", encoding="utf-8") as file:
            categories_params = yaml.safe_load(file)["ontology"]["categories"]

        for category_params in categories_params:
            if category_params.get("id", None) == category_name:
                return category_params.get("name")

        return None

    def get_all_categories_examples(self) -> dict[str, list[str]]:
        with open(self.kb / "category_examples.yml", "r", encoding="utf-8") as file:
            return yaml.safe_load(file)["category_examples"]

    def get_categories_rules(self, cat_name: str) -> dict[str, list[str, str, str]]:
        with open(self.kb / "rules.yml", "r", encoding="utf-8") as file:
            return yaml.safe_load(file)["rules"][cat_name]

    def get_waste_for_cat(self, cat_name: str) -> int:
        with open(self.kb / "wastes.yml", "r", encoding="utf-8") as file:
            return yaml.safe_load(file)["wastes"][cat_name]

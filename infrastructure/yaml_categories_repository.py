import yaml

import config
from repository.base_categories_repository import BaseCategoriesRepositry


class YamlCategoriesRepository(BaseCategoriesRepositry):
    def __init__(self, kb_path: str):
        self.kb = kb_path

    def get_all_categories(self) -> dict:
        with open(self.kb, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)["ontology"]['categories']
        
    def get_all_keywords(self):
        with open(self.kb, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)["ontology"]["lexicon"] 
            
    def get_lexicon(self):
        with open(self.kb, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)["lexicon"]

    def keyword_search(self, keyword: str) -> str | None:
        output_category = None
        categories = self.get_all_keywords()
        for category, data in categories.items(): 
            if keyword in data["keywords"]:
                output_category = category

        return output_category

    def save_category(self, category_name: str) -> None:
        print("...")


if __name__ == "__main__":
    categor = YamlCategoriesRepository(config.YAML_CATEGORIES)
    print(categor.get_all_categories())

from repository.base_categories_repository import BaseCategoriesRepositry


class GetCategories:
    def __init__(self, repository: BaseCategoriesRepositry):
        self.repo = repository
        
    def get_categories_names(self):
        data = self.repo.get_all_categories()
        categories = []
        for category in data:
            for key, value in category.items():
                if key == "name":
                    categories.append(value)
                    
        return categories
# app/support/category/repository.py
class CategoryRepository:
    def __init__(
            self, category_id: int | None = None,
            name: str | None = None,
            description: str | None = None,
            count_drink: int = 0
            ):
        self.id = category_id
        self.name = name
        self.description = description
        # self.count_drink = count_drink

    def to_dict(self) -> dict:
        data = {'id': self.id, 'name': self.name,
                'description': self.description,
                # 'count_drink': self.count_drink
                }
        # Создаем копию словаря, чтобы избежать изменения
        # словаря во время итерации
        filtered_data = {key: value for key, value in data.items() if
                         value is not None}
        return filtered_data

# app/support/drink/repository.py

class DrinkRepository:
    def __init__(
            self, drink_id: int | None = None,
            title: str | None = None,
            subtitle: str | None = None,
            category_id: int | None = None
            ):
        self.id = drink_id
        self.title = title
        self.subtitle = subtitle
        self.category_id = category_id

    def to_dict(self) -> dict:
        data = {'id': self.id,
                'title': self.title,
                'subtitle': self.subtitle,
                'category_id': self.category_id}
        # Создаем копию словаря, чтобы избежать изменения
        # словаря во время итерации
        filtered_data = {key: value for key, value in data.items() if
                         value is not None}
        return filtered_data

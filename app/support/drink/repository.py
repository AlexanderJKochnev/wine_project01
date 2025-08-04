# app/support/drink/repository.py
from app.core.repositories.sqlalchemy_repository import SqlAlchemyRepository
from app.support.drink.models import Drink


class DrinkRepository(SqlAlchemyRepository):
    model = Drink

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

# app/support/category/repository.py
from app.core.repositories.sqlalchemy_repository import SqlAlchemyRepository
from app.support.category.models import Category


class CategoryRepository(SqlAlchemyRepository):
    model = Category

    def to_dict(self):
        data = self.model.model_dump()
        filtered_data = {key: value for key, value in data.items() if value is not None}
        return filtered_data

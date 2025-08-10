# app/support/template/repository.py
"""
замени Template на имя модели в единственном числе с сохранением регистра
"""

from app.support.template.models import Template
from app.core.repositories.sqlalchemy_repository import Repository
from sqlalchemy.orm import selectinload
from sqlalchemy import select
# from app.core.config.database.db_noclass import get_db


# TemplateRepository = RepositoryFactory.get_repository(Template)
class TemplateRepository(Repository):
    model = Template

    def get_query(self):
        # Добавляем загрузку связи с relationships
        return select(Template).options(selectinload(Template.category))

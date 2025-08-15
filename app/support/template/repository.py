# app/support/template/repository.py
"""
    если есть поля с relationships manytoone заполни актуальной информацией процедуру get_query
    для примера см. app/support/drink/repository.py
    ЕСЛИ ТАКИХ ПОЛЕЙ НЕТ - УДАЛИ ЭТУ ПРОЦЕДУРУ ПОЛНОСТЬЮ
"""

from app.support.template.model import Template
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

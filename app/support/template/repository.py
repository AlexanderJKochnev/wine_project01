# app/support/template/repository.py
"""
    если есть поля с relationships manytoone заполни актуальной информацией процедуру get_query
    для примера см. app/support/drink/repository.py
    ЕСЛИ ТАКИХ ПОЛЕЙ НЕТ - УДАЛИ ЭТУ ПРОЦЕДУРУ ПОЛНОСТЬЮ
"""

from app.support.region.model import Template
from app.core.repositories.sqlalchemy_repository import Repository
from sqlalchemy.orm import joinedload
from sqlalchemy import select


class TemplateRepository(Repository):
    model = Template

    @classmethod
    def get_query(cls):
        # Добавляем загрузку связи с relationships
        return select(Template).options(joinedload(Template.country))

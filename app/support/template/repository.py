# app/support/template/repository.py
"""
замени Template на имя модели в единственном числе с сохранением регистра
"""

from app.core.repositories.repo_factory import RepositoryFactory
from app.support.template.models import Template


TemplateRepository = RepositoryFactory.get_repository(Template)

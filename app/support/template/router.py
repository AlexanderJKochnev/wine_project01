# app/support/template/router.py
"""
замени Template на имя модели в единственном числе с сохранением регистра
"""
from app.core.repositories.repo_factory import RepositoryFactory
from app.support.template.models import Template

CategoryRepository = RepositoryFactory.get_repository(Template)


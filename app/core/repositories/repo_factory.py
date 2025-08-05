# app/core/repositories/repo_factory.py
"""
    фабрика для генерации репозиториев на базе model
"""
from typing import Dict, Type, TypeVar
from sqlalchemy.orm import DeclarativeMeta
from weakref import WeakValueDictionary
from app.core.repositories.sqlalchemy_repo2 import Repository


ModelType = TypeVar("ModelType", bound=DeclarativeMeta)


class RepositoryFactory:
    """
    Фабрика репозиториев с кэшированием.
    Один репозиторий — на одну модель (синглтон).
    Использует слабые ссылки, чтобы не мешать сборке мусора.
    """
    _repositories: Dict[Type[DeclarativeMeta], Repository] = WeakValueDictionary()

    @classmethod
    def get_repository(cls, model: Type[ModelType]) -> Repository[ModelType]:
        """
        Возвращает закэшированный репозиторий для модели.
        Если нет — создаёт и сохраняет.
        """
        if model not in cls._repositories:
            repo = Repository(model)
            cls._repositories[model] = repo
        return cls._repositories[model]

    @classmethod
    def clear(cls):
        """Очистить кэш (для тестов)."""
        cls._repositories.clear()

    @classmethod
    def get_all_repositories(cls):
        """Получить все активные репозитории."""
        return dict(cls._repositories)

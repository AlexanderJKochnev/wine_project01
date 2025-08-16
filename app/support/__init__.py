# app/support/__init__.py
"""
    порядок импорта определяет порядок загрузки
    модели с ForeignKey должны должны быть выше моделей на которые они ссылаются
"""

from app.support.drink.model import Drink  # NOQA F401
from app.support.category.model import Category  # NOQA F401
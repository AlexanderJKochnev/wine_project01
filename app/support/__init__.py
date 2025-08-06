# app/support/__init__.py
"""
    порядок импорта определяет порядок загрузки
    модели с ForeignKey должны должны быть выше моделей на которые они ссылаются
"""

from app.support.drink.models import Drink  # NOQA F401
from app.support.category.models import Category  # NOQA F401
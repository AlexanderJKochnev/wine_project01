# app/support/__init__.py
"""
    порядок импорта определяет порядок загрузки
    модели с ForeignKey должны должны быть выше моделей на которые они ссылаются
"""
from app.support.varietal.model import Varietal  # NOQA F401
from app.support.item.model import Item  # NOQA F401
from app.support.drink.model import Drink  # NOQA F401
from app.support.category.model import Category  # NOQA F401
from app.support.subcategory.model import Subcategory  # NOQA F401
from app.support.food.model import Food  # NOQA F401
from app.support.superfood.model import Superfood  # NOQA F401
from app.support.subregion.model import Subregion  # NOQA F401
from app.support.region.model import Region  # NOQA F401
from app.support.country.model import Country  # NOQA F401
from app.support.sweetness.model import Sweetness  # NOQA F401
from app.support.warehouse.model import Warehouse  # NOQA F401
from app.support.customer.model import Customer  # NOQA F401
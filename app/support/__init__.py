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

from app.support.varietal.schemas import VarietalRead  # NOQA F401
from app.support.item.schemas import ItemRead  # NOQA F401
from app.support.drink.schemas import DrinkRead  # NOQA F401
from app.support.category.schemas import CategoryRead  # NOQA F401
from app.support.subcategory.schemas import SubcategoryRead  # NOQA F401
from app.support.food.schemas import FoodRead  # NOQA F401
from app.support.superfood.schemas import SuperfoodRead  # NOQA F401
from app.support.region.schemas import RegionRead  # NOQA F401
from app.support.subregion.schemas import SubregionRead  # NOQA F401
from app.support.country.schemas import CountryRead  # NOQA F401
from app.support.sweetness.schemas import SweetnessRead  # NOQA F401
from app.support.warehouse.schemas import WarehouseRead  # NOQA F401
from app.support.customer.schemas import CustomerRead  # NOQA F401

from app.support.category.service import CategoryService  # NOQA F401
from app.support.country.service import CountryService  # NOQA F401
from app.support.item.service import ItemService  # NOQA F401
from app.support.customer.service import CustomerService  # NOQA F401
from app.support.drink.service import DrinkService  # NOQA F401
from app.support.food.service import FoodService  # NOQA F401
from app.support.region.service import RegionService  # NOQA F401
from app.support.subcategory.service import SubcategoryService  # NOQA F401
from app.support.subregion.service import SubregionService  # NOQA F401
from app.support.superfood.service import SuperfoodService  # NOQA F401
from app.support.sweetness.service import SweetnessService  # NOQA F401
from app.support.varietal.service import VarietalService  # NOQA F401
# from app.support.warehouse.service import WarehouseService  # NOQA F401
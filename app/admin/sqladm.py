# app/admin/sqladmin.md
# from wtforms.widgets import TextArea
from app.admin.core import AutoModelView
# --------подключение моделей-----------
from app.support.drink.model import Drink
from app.support.category.model import Category
from app.support.country.model import Country
from app.support.customer.model import Customer
from app.support.warehouse.model import Warehouse
from app.support.food.model import Food
from app.support.item.model import Item
from app.support.region.model import Region
from app.support.color.model import Color
from app.support.sweetness.model import Sweetness


class DrinkAdmin(AutoModelView, model=Drink):
    # column_searchable_list = [Drink.name, Drink.name_ru]
    # column_sortable_list = [Drink.id, Drink.name, Drink.category]
    # form_columns = [Drink.name, Drink.subtitle,
    #                 Drink.description, Drink.category]
    # form_excluded_columns = ['created_at', 'updated_at', 'pk']
    pass


class CategoryAdmin(AutoModelView, model=Category):
    name = "Category"
    name_plural = "Categories"


class CountryAdmin(AutoModelView, model=Country):
    name = 'Country'
    name_plural = 'Countries'


class CustomerAdmin(AutoModelView, model=Customer):
    pass


class WarehouseAdmin(AutoModelView, model=Warehouse):
    pass


class FoodAdmin(AutoModelView, model=Food):
    pass


class ItemAdmin(AutoModelView, model=Item):
    pass


class RegionAdmin(AutoModelView, model=Region):
    pass


class SweetnessAdmin(AutoModelView, model=Sweetness):
    name = 'Sweetness'
    name_plural = 'Sweetness type'


class ColorAdmin(AutoModelView, model=Color):
    pass

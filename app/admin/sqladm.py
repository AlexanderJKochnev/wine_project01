# app/admin/sqladmin.md
# from wtforms.widgets import TextArea
from app.admin.core import AutoModelView
# --------подключение моделей-----------
from app.support.drink.models import Drink
from app.support.category.models import Category
from app.support.country.models import Country
from app.support.customer.models import Customer
from app.support.warehouse.models import Warehouse
from app.support.food.models import Food


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

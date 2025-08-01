# app/admin/sqladmin.py
# from sqladmin import ModelView
from app.support.drink.models import Drink
from app.support.category.models import Category
from app.admin.core import AutoModelView


class DrinkAdmin(AutoModelView, model=Drink):
    # column_list = [Drink.id, Drink.title, Drink.category, Drink.subtitle]
    column_searchable_list = [Drink.name]
    column_sortable_list = [Drink.id, Drink.name, Drink.category]

    # Это поле будет отображаться как выпадающий список
    form_columns = [Drink.name, Drink.subtitle,
                    Drink.description, Drink.category]


class CategoryAdmin(AutoModelView, model=Category):
    name = "Category"
    name_plural = "Categories"
    # column_list = ['count_drink', 'id', 'name']
    # # column_list = [Category.id, Category.name]  # , Category.description]
    # form_columns = [Category.name, Category.description]
    # # Настройка внешнего вида полей формы
    """form_widget_args = \
        {"description": {"class": "sqladmin-textarea",
                         "style": "min-height: 150px; width: 100%;",
                         "placeholder": "Enter detailed description...", }}
"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

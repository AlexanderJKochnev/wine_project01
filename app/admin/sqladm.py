# app/admin/sqladmin.py
from sqladmin import ModelView
from app.support.drink.models import Drink
from app.support.category.models import Category


class DrinkAdmin(ModelView, model=Drink):
    column_list = [Drink.id, Drink.title, Drink.category, Drink.subtitle]
    column_searchable_list = [Drink.title]
    column_sortable_list = [Drink.id, Drink.title, Drink.category]

    # Это поле будет отображаться как выпадающий список
    form_columns = [Drink.title, Drink.subtitle,
                    Drink.description, Drink.category]


class CategoryAdmin(ModelView, model=Category):
    column_list = [Category.id, Category.name, Category.description]
    form_columns = [Category.name, Category.description]

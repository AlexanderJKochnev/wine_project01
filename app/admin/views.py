# app.admin.views.py
from sqlalchemy.orm import joinedload, selectinload
from starlette.requests import Request
from starlette_admin.contrib.sqla import ModelView
from starlette_admin.fields import BooleanField, DateTimeField, IntegerField, PasswordField, StringField

from app.admin.core import FieldsCore


class UserAdminView(ModelView):
    # Явно декларируем поля для форм и таблиц с правильными типами из starlette_admin.fields
    fields = [IntegerField("id", label="ID"), StringField("username", label="Имя пользователя", required=True),
              StringField("email", label="Email"),
              PasswordField("hashed_password", label="Пароль", exclude_from_list=True),
              BooleanField("is_active", label="Активен"),
              BooleanField("is_superuser", label="Суперпользователь"),
              DateTimeField("delete_time", label="Дата удаления")]

    # Исключаем автоинкрементный ID из формы создания/редактирования
    form_exclude_fields = ["id"]

    # Включаем живой поиск по ключевым полям в таблице
    searchable_fields = ["username", "email"]

    # Разрешаем фильтрацию по статусам
    filterable_fields = ["is_active", "is_superuser"]


core_fields = FieldsCore()


class HandbookView(ModelView):
    pk_attr = "id"
    fields = core_fields()
    print(f'{fields=}')


class TestView(ModelView):
    fields = [IntegerField("id", label="ID"),
              StringField("name", label="Name", required=True),
              ]
# app.admin.views.py
from sqlalchemy.orm import selectinload
from starlette_admin.contrib.sqla import ModelView
from starlette_admin.fields import BooleanField, DateTimeField, IntegerField, PasswordField, StringField


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


class SomeView(ModelView):
    pk_attr = "id"


class CategoryView(ModelView):
    # Переопределяем базовое выражение SELECT для этой таблицы
    def select_expr(self, request):
        # Берем стандартный SELECT запрос админки и добавляем жадную загрузку связи
        # Замените 'author' на точное имя вашего поля с back_populates
        return super().select_expr(request).options(selectinload(self.model.subcategories))
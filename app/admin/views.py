# app.admin.views.py
from starlette_admin.contrib.sqla import ModelView
from starlette_admin.fields import BooleanField, ColorField, DateTimeField, HasOne, IntegerField, PasswordField, \
    StringField

from app.admin.core import HandBooksFieldsCore


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


core_fields = HandBooksFieldsCore()


class BaseModelView(ModelView):
    async def render(self, request, obj, field):
        # Если поле - это отношение, пробуем получить строковое представление
        if isinstance(field, HasOne) and obj is not None:
            value = getattr(obj, field.identity, None)
            if value is not None and hasattr(value, '__str__'):
                return str(value)
        return await super().render(request, obj, field)


class HandbookView(ModelView):
    pk_attr = "id"
    fields = core_fields()


class SubcategoryView(ModelView):
    pk_attr = "id"
    fields = core_fields()
    fields.insert(2, HasOne('category', identity='category'))


class CategoryView(ModelView):
    pk_attr = "id"
    fields = core_fields()
    fields.insert(1, ColorField('color', label='Color',
                                exclude_from_list=True,
                                # render_function_key="renderColor",
                                display_template="displays/color.html",
                                ))


class TestView(ModelView):
    fields = [IntegerField("id", label="ID"),
              StringField("name", label="Name", required=True),
              ]

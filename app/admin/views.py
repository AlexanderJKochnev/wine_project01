# app.admin.views.py
from typing import Any, List

from starlette.requests import Request
from starlette_admin.contrib.sqla import ModelView
from starlette_admin.fields import BooleanField, ColorField, DateTimeField, HasMany, HasOne, IntegerField, \
    PasswordField, StringField

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


core_fields = HandBooksFieldsCore(0)
drink_fields = HandBooksFieldsCore(1)


class BaseModelView(ModelView):
    async def render(self, request, obj, field):
        # Если поле - это отношение, пробуем получить строковое представление
        if isinstance(field, HasOne) and obj is not None:
            value = getattr(obj, field.identity, None)
            if value is not None and hasattr(value, '__str__'):
                return str(value)
        return await super().render(request, obj, field)


class SubcategoryView(ModelView):
    pk_attr = "id"
    fields = core_fields()
    fields.insert(2, HasOne('category', identity='category', searchable=True, orderable=True))
    fields.insert(
        1, ColorField(
            'color', label='Color', display_template="displays/color.html", help_text='Цвет фона на изображении'
        )
    )
    fields.insert(3, HasMany('drinks', identity='drink', exclude_from_list=True, exclude_from_detail=True))

    """
    async def get_list_query(self, request):
        # Переопределяем запрос для списка с жадной загрузкой связанных данных
        query = select(self.model).options(noload(self.model.drinks))
        # query = await super().get_list_query(request)
        # Загружаем все необходимые связи для Select2
        return query.options(
            joinedload(Subcategory.category)  # Загружаем категорию
            # Если есть более глубокие связи, например category.region:
            # selectinload(Subcategory.category).selectinload(Category.region)
        )
    """

    async def find_by_pks(self, request: Request, pks: List[Any]) -> List[Any]:
        from loguru import logger
        logger.warning(f'subcategory ============== {pks=}, {type(pks)=}, {self._pk_coerce=}')
        return await super().find_by_pks(request, pks)


class CategoryView(ModelView):
    pk_attr = "id"
    fields = core_fields()
    fields.insert(1, ColorField('color',
                                label='Color',
                                display_template="displays/color.html",
                                help_text='Цвет фона на изображении'
                                ))
    fields.insert(3, HasMany('subcategories', identity='subcategory', exclude_from_list=True))


class CountryView(ModelView):
    pk_attr = "id"
    fields = core_fields()
    fields.insert(3, HasMany('regions', identity='region', exclude_from_list=True))


class RegionView(ModelView):
    pk_attr = "id"
    fields = core_fields()
    fields.insert(2, HasOne('country', identity='country'))
    fields.insert(3, HasMany('subregions', identity='subregion', exclude_from_list=True))


class SubregionView(ModelView):
    pk_attr = "id"
    fields = core_fields()
    fields.insert(2, HasOne('region', identity='region'))
    fields.insert(3, HasMany('sites', identity='site', exclude_from_list=True))


class SiteView(ModelView):
    pk_attr = "id"
    fields = core_fields()
    fields.insert(2, HasOne('subregion', identity='subregion'))
    fields.insert(3, HasMany('drinks', identity='drink', exclude_from_list=True, exclude_from_detail=True))


class ParcelView(ModelView):
    pk_attr = "id"
    fields = core_fields()
    fields.insert(3, HasMany('drinks', identity='drink', exclude_from_list=True, exclude_from_detail=True))


class ProducerTitleView(ModelView):
    pk_attr = "id"
    fields = core_fields()
    fields.insert(3, HasMany('producers', identity='producer', exclude_from_list=True))


class ProducerView(ModelView):
    pk_attr = "id"
    fields = core_fields()
    fields.insert(2, HasOne('producertitle', identity='producertitle'))
    fields.insert(3, HasMany('drinks', identity='drink', exclude_from_list=True, exclude_from_detail=True))

# source


class SourceView(ModelView):
    pk_attr = "id"
    fields = core_fields()
    fields.insert(3, HasMany('drinks', identity='drink', exclude_from_list=True, exclude_from_detail=True))

    async def find_by_pks(self, request: Request, pks: List[Any]) -> List[Any]:
        from loguru import logger
        logger.warning(f'source ========== {pks=}, {type(pks)=}')
        return await super().find_by_pks(request, pks)


class SuperFoodView(ModelView):
    pk_attr = "id"
    fields = core_fields()
    fields.insert(3, HasMany('foods', identity='food', exclude_from_list=True))


class FoodView(ModelView):
    pk_attr = "id"
    fields = core_fields()
    fields.insert(2, HasOne('superfood', identity='superfood'))
    fields.insert(3, HasMany('drinks', identity='drink', exclude_from_list=True, exclude_from_detail=True))


class VarietalView(ModelView):
    pk_attr = "id"
    fields = core_fields()
    fields.insert(3, HasMany('drinks', identity='drink', exclude_from_list=True, exclude_from_detail=True))


class HandbookView(ModelView):
    pk_attr = "id"
    fields = core_fields()


class DrinkView(ModelView):
    pk_attr = "id"
    fields = drink_fields()
    extra_fields = [StringField('display_name', label='Полное наименование', exclude_from_list=True),
                    HasOne('subcategory', identity='subcategory'),
                    HasOne('site', identity='site', exclude_from_list=True),
                    HasOne('parcel', identity='parcel', exclude_from_list=True),
                    HasOne('producer', identity='producer'),
                    HasOne('source', identity='source', exclude_from_list=True),
                    HasOne('vintageconfig', identity='vintageconfig', exclude_from_list=True),
                    HasOne('classification', identity='classification', exclude_from_list=True),
                    HasOne('designation', identity='designation', exclude_from_list=True),
                    HasOne('glassware', identity='glassware', exclude_from_list=True),
                    HasOne('scale', identity='scale', exclude_from_list=True),
                    HasOne('body', identity='body', exclude_from_list=True),
                    ]
    fields[3:3] = extra_fields


class TestView(ModelView):
    fields = [IntegerField("id", label="ID"),
              StringField("name", label="Name", required=True),
              ]


class ItemView(ModelView):
    fields = ["id", "drink", "vol", "price", "seaweed_fids"]
    select_related = ["subcategory", "subcategory.category"]

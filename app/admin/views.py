# app.admin.views.py
from typing import Any, Dict, List, Optional, Sequence, Type, Union

import anyio
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, noload, Session
from starlette.requests import Request
from starlette_admin import RequestAction
from starlette_admin.contrib.sqla import ModelView as OriginModelView
from starlette_admin.contrib.sqla.converters import BaseSQLAModelConverter
from starlette_admin.fields import BooleanField, ColorField, DateTimeField, HasMany, HasOne, IntegerField, \
    PasswordField, RelationField, StringField

from app.admin.core import HandBooksFieldsCore
from app.support import Category


class ModelView(OriginModelView):
    def __init__(self,
                 model: Type[Any],
                 icon: Optional[str] = None,
                 name: Optional[str] = None,
                 label: Optional[str] = None,
                 identity: Optional[str] = None,
                 converter: Optional[BaseSQLAModelConverter] = None,
                 ):
        super().__init__(model, icon, name, label, identity, converter)
        print(f'==={name=}======{self.sortable_fields=}')


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
    fields.insert(2, HasOne('category', identity='category', searchable=True))
    fields.insert(
        1, ColorField(
            'color', label='Color', display_template="displays/color.html", help_text='Цвет фона на изображении'
        )
    )
    fields.insert(3, HasMany('drinks', identity='drink', exclude_from_list=True, exclude_from_detail=True,
                             orderable=True
                             ))
    # sortable_fields = ["id", "name", "category"]
    sortable_field_mapping = {"category": Category.name,
                              }

    async def find_by_pks(self, request: Request, pks: List[Any]) -> List[Any]:
        session = request.state.session

        try:
            int_pks = [int(pk) for pk in pks]
        except (ValueError, TypeError):
            int_pks = pks

        stmt = (super().get_list_query(request).where(self.model.id.in_(int_pks)).options(
                joinedload(self.model.category),  # Принудительно асинхронно соединяем категорию
                noload(self.model.drinks)  # По-прежнему намертво блокируем напитки
                ))

        result = await session.execute(stmt)
        return result.scalars().unique().all()

    def get_list_query(self, request: Request = None):
        """
        На всякий случай отключаем JOIN и для обычной таблицы со списком подкатегорий
        """
        query = super().get_list_query(request) if request else super().get_list_query()
        return query.options(noload(self.model.drinks))

    async def find_all(
            self, request: Request, skip: int = 0, limit: int = 100, where: Union[Dict[str, Any], str, None] = None,
            order_by: Optional[List[str]] = None, ) -> Sequence[Any]:
        session: Union[Session, AsyncSession] = request.state.session

        # 1. Берем базовый запрос из get_list_query (там уже должен быть noload на drinks)
        stmt = self.get_list_query(request).offset(skip)
        if limit > 0:
            stmt = stmt.limit(limit)

        # Получаем класс модели Категории динамически
        CategoryModel = self.model.category.property.mapper.class_

        # 2. Модифицируем логику фильтрации WHERE
        if where is not None:
            if isinstance(where, dict):
                # Если это стандартный поиск по полям, проверяем, не ищет ли админка по тексту
                # Обычно для Select2 приходит что-то вроде {"name": {"ilike": "%текст%"}}
                search_term = None
                if "name" in where and isinstance(where["name"], dict):
                    search_term = where["name"].get("ilike") or where["name"].get("like")

                if search_term:
                    # Если обнаружен текстовый поиск, делаем JOIN и перезаписываем условие на OR
                    stmt = stmt.join(self.model.category)
                    where_clause = or_(
                        self.model.name.ilike(search_term), CategoryModel.name.ilike(search_term)
                    )
                else:
                    # Во всех остальных случаях используем оригинальный построитель
                    from starlette_admin.contrib.sqla.helpers import build_query
                    where_clause = build_query(where, self.model)
            else:
                # Если пришла чистая строка (Глобальный полнотекстовый поиск админки)
                stmt = stmt.join(self.model.category)
                search_pattern = f"%{where}%"
                where_clause = or_(
                    self.model.name.ilike(search_pattern), CategoryModel.name.ilike(search_pattern)
                )

            stmt = stmt.where(where_clause)

        # 3. Оригинальная сортировка
        stmt = self.build_order_clauses(request, order_by or [], stmt)

        # 4. Оригинальная загрузка связей БЕЗ тяжелого drinks
        # Мы явно пропускаем поле 'drinks', чтобы админка не сделала ему joinedload
        for field in self.get_fields_list(request, RequestAction.LIST):
            if isinstance(field, RelationField):
                if field.name == "drinks":
                    stmt = stmt.options(noload(self.model.drinks))
                else:
                    stmt = stmt.options(joinedload(getattr(self.model, field.name)))

        # 5. Оригинальное выполнение запроса
        if isinstance(session, AsyncSession):
            return (await session.execute(stmt)).scalars().unique().all()
        return ((await anyio.to_thread.run_sync(session.execute, stmt)).scalars().unique().all())


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
    fields.insert(2, HasOne('country', identity='country', orderable=True))
    fields.insert(3, HasMany('subregions', identity='subregion', exclude_from_list=True))


class SubregionView(ModelView):
    pk_attr = "id"
    fields = core_fields()
    fields.insert(2, HasOne('region', identity='region', orderable=True))
    fields.insert(3, HasMany('sites', identity='site', exclude_from_list=True))


class SiteView(ModelView):
    pk_attr = "id"
    fields = core_fields()
    fields.insert(2, HasOne('subregion', identity='subregion', orderable=True))
    fields.insert(3, HasMany('drinks', identity='drink', exclude_from_list=True, exclude_from_detail=True))

    def _get_geo_options(self):
        """
        Вспомогательный метод для построения правильной и быстрой загрузки.
        Загружает всю цепочку за 1 запрос и блокирует тяжелые напитки.
        """
        return [  # Цепочка жадной загрузки: Site -> Subregion -> Region -> Country
            joinedload(self.model.subregion).joinedload(
                self.model.subregion.property.mapper.class_.region
            ).joinedload(self.model.subregion.property.mapper.class_.region.property.mapper.class_.country),

            # Намертво отключаем загрузку напитков, чтобы избежать декартова произведения
            noload(self.model.drinks)]

    async def find_by_pks(self, request: Request, pks: List[Any]) -> List[Any]:
        """
        Метод для точечных запросов (например, ?select2=true&pks=3)
        """
        session = request.state.session

        try:
            int_pks = [int(pk) for pk in pks]
        except (ValueError, TypeError):
            int_pks = pks

        stmt = (super().get_list_query(request).where(self.model.id.in_(int_pks)).options(*self._get_geo_options())
                # Применяем оптимизацию связей
                )

        result = await session.execute(stmt)
        return result.scalars().unique().all()

    async def find_all(
            self, request: Request, skip: int = 0, limit: int = 100, where: Union[Dict[str, Any], str, None] = None,
            order_by: Optional[List[str]] = None, ) -> Sequence[Any]:
        session: Union[Session, AsyncSession] = request.state.session

        stmt = self.get_list_query(request).offset(skip)
        if limit > 0:
            stmt = stmt.limit(limit)

        # Динамически получаем классы связанных моделей для построения JOIN и условий поиска
        SubregionModel = self.model.subregion.property.mapper.class_
        RegionModel = SubregionModel.region.property.mapper.class_
        CountryModel = RegionModel.country.property.mapper.class_

        # Перехватываем текстовый поиск
        if where is not None:
            if isinstance(where, dict):
                search_term = None
                if "name" in where and isinstance(where["name"], dict):
                    search_term = where["name"].get("ilike") or where["name"].get("like")

                if search_term:
                    # Для сквозного поиска делаем последовательные JOIN всех таблиц
                    stmt = stmt.join(self.model.subregion).join(SubregionModel.region).join(RegionModel.country)

                    where_clause = or_(
                        self.model.name.ilike(search_term),       # Поиск по имени сайта
                        SubregionModel.name.ilike(search_term),   # Поиск по субрегиону
                        RegionModel.name.ilike(search_term),      # Поиск по региону
                        CountryModel.name.ilike(search_term)      # Поиск по стране
                    )
                else:
                    from starlette_admin.contrib.sqla.helpers import build_query
                    where_clause = build_query(where, self.model)
            else:
                # Глобальный полнотекстовый поиск (пришла чистая строка)
                stmt = stmt.join(self.model.subregion) \
                    .join(SubregionModel.region) \
                    .join(RegionModel.country)
                search_pattern = f"%{where}%"
                where_clause = or_(
                    self.model.name.ilike(search_pattern),
                    SubregionModel.name.ilike(search_pattern),
                    RegionModel.name.ilike(search_pattern),
                    CountryModel.name.ilike(search_pattern)
                )

            stmt = stmt.where(where_clause)

        stmt = self.build_order_clauses(request, order_by or [], stmt)

        # Перезаписываем автоматические joinedload админки, защищая поле 'drinks'
        for field in self.get_fields_list(request, RequestAction.LIST):
            if isinstance(field, RelationField):
                if field.name == "drinks":
                    stmt = stmt.options(noload(self.model.drinks))
                else:
                    # Для всех остальных полей оставляем дефолтное поведение,
                    # но подмешиваем наши оптимизированные гео-опции
                    stmt = stmt.options(joinedload(getattr(self.model, field.name)))

        # Принудительно накатываем наши гео-опции поверх структуры запроса
        stmt = stmt.options(*self._get_geo_options())

        if isinstance(session, AsyncSession):
            return (await session.execute(stmt)).scalars().unique().all()
        return (
            (await anyio.to_thread.run_sync(session.execute, stmt))
            .scalars()
            .unique()
            .all()
        )


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

# app/admin/core.py
from sqladmin import ModelView
from sqlalchemy.sql.sqltypes import Integer, String, Text, Boolean
from sqlalchemy import inspect
from typing import Set, List, Any, Tuple
from functools import cached_property
from sqlalchemy.orm import RelationshipProperty
from starlette.requests import Request


class AutoModelView(ModelView):
    """
    Автоматически формирует column_list из всех колонок модели,
    кроме исключённых. Работает корректно с sqladmin.
    """
    # поля которые будут выведены в списке
    # column_list = ["name", "name_ru"]
    # поля по которым будет производиться поиск
    column_searchable_list = ['name', 'name_ru']
    # поля, которые исключаем по умолчанию
    exclude_columns: Set[str] = {"password", "secret", "api_key",
                                 "token", "salt", "hashed_password", "created_at",
                                 "updated_at", "deleted_at", "is_deleted", "description", "id"}
    # поля сортировки
    column_sortable_list = ['name', 'name_ru']
    # DETAIL VIEW
    # поля исключаемые из detail view
    column_details_exclude_list = {'created_at', 'updated_at', 'pk', 'id'}
    # поля, которые исключаются из формы
    form_excluded_columns = {'created_at', 'updated_at', 'pk'}

    # порядок вывода колонок
    sort_columns: Tuple[str] = ("primary_key", "index", "nullable",)
    type_priority: Tuple[Any] = (String, Integer)
    type_excluded: Tuple[Any] = (Text,)
    # Включать ли первичный ключ в список
    include_pk_in_list: bool = False

    @cached_property
    def _model_columns(self) -> List[str]:
        """Возвращает список атрибутов модели для column_list."""
        mapper = inspect(self.model)
        columns: List[str] = []
        tmp: dict = {}
        rel: List[Any] = []

        for attr in mapper.attrs:
            if (hasattr(attr, "columns") and attr.key not in self.exclude_columns):
                # Только колонки (не relationships)
                col = attr.columns[0]
                # Исключить типы self.type_excluded
                if type(getattr(col, 'type')) in self.type_excluded:
                    continue
                x = sum(
                    (False if getattr(col, key) is None else getattr(col, key)) * 2 ** n for n, key in
                    enumerate(reversed(self.sort_columns))
                )
                y = sum(
                    isinstance(getattr(col, 'type'), a) * 2 ** n for n, a in enumerate(reversed(self.type_priority))
                )
                tmp[attr.key] = (attr, x, y)

            if isinstance(attr, RelationshipProperty):
                # relationships
                if (attr.direction.name == "MANYTOONE" and attr.key not in self.exclude_columns):
                    rel.append(attr)

        # замена id на relationship
        for item in rel:
            val = tmp.get(f'{item.key}_id')
            if val:
                tmp[f'{item.key}_id'] = (item, val[1], val[2])
            else:
                tmp[item.key] = (item, 0, 0)

        # сортировка
        tmp1 = [(*val, key) for key, val in tmp.items()]
        sorted_columns = sorted(tmp1, key=lambda a: (a[1], a[2], a[3]))
        columns = [a[3] for a in reversed(sorted_columns)]

        return columns

    @cached_property
    def _form_columns(self) -> List[str]:
        """Формирует список полей для формы с заданным порядком."""
        mapper = inspect(self.model)
        columns = []

        # Группируем поля по категориям
        text_fields = []
        bool_fields = []
        rel_fields = []
        memo_fields = []
        other_fields = []

        for attr in mapper.attrs:
            if attr.key in self.form_excluded_columns or attr.key in self.exclude_columns:
                continue

            if isinstance(attr, RelationshipProperty):
                if attr.direction.name == "MANYTOONE":
                    rel_fields.append(attr.key)
                continue

            if hasattr(attr, "columns"):
                col = attr.columns[0]

                # Пропускаем поля с default/autoincrement
                if col.default is not None or col.autoincrement:
                    continue

                # Получаем тип поля
                col_type = col.type.__class__ if hasattr(col.type, '__class__') else type(col.type)

                if issubclass(col_type, Text):
                    memo_fields.append(attr.key)
                elif issubclass(col_type, Boolean):
                    bool_fields.append(attr.key)
                elif issubclass(col_type, String):
                    # Сначала non-nullable поля
                    if not col.nullable:
                        text_fields.insert(0, attr.key)
                    else:
                        text_fields.append(attr.key)
                else:
                    # Другие типы (Integer и т.д.)
                    if not col.nullable:
                        other_fields.insert(0, attr.key)
                    else:
                        other_fields.append(attr.key)

        # Формируем итоговый порядок
        columns.extend(text_fields)
        columns.extend(other_fields)  # Добавляем другие типы после String
        columns.extend(bool_fields)
        columns.extend(rel_fields)
        columns.extend(memo_fields)

        return columns

    @cached_property
    def _column_details_list(self) -> List[str]:
        """Формирует список полей для детального просмотра."""
        mapper = inspect(self.model)
        columns = []

        # Группируем поля по категориям
        text_fields = []
        bool_fields = []
        rel_fields = []
        memo_fields = []
        other_fields = []

        for attr in mapper.attrs:
            if attr.key in self.column_details_exclude_list or attr.key in self.exclude_columns:
                continue

            if isinstance(attr, RelationshipProperty):
                if attr.direction.name in ["MANYTOONE", "ONETOMANY"]:
                    rel_fields.append(attr.key)
                continue

            if hasattr(attr, "columns"):
                col = attr.columns[0]

                # Получаем тип поля
                col_type = col.type.__class__ if hasattr(col.type, '__class__') else type(col.type)

                if issubclass(col_type, Text):
                    memo_fields.append(attr.key)
                elif issubclass(col_type, Boolean):
                    bool_fields.append(attr.key)
                elif issubclass(col_type, String):
                    # Сначала non-nullable поля
                    if not col.nullable:
                        text_fields.insert(0, attr.key)
                    else:
                        text_fields.append(attr.key)
                else:
                    # Другие типы (Integer и т.д.)
                    if not col.nullable:
                        other_fields.insert(0, attr.key)
                    else:
                        other_fields.append(attr.key)

        # Формируем итоговый порядок
        columns.extend(text_fields)
        columns.extend(other_fields)
        columns.extend(bool_fields)
        columns.extend(rel_fields)
        columns.extend(memo_fields)

        return columns

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Устанавливаем списки, если не заданы явно
        if not cls.column_list:
            cls.column_list = cls._model_columns
        if not cls.column_details_list:
            cls.column_details_list = cls._column_details_list
        if not cls.form_columns:
            cls.form_columns = cls._form_columns


class BaseAdmin(ModelView):
    """Базовый класс для админ панели с проверкой прав"""

    async def is_accessible(self, request: Request) -> bool:
        # Проверяем, авторизован ли пользователь
        token = request.session.get("admin_token")
        if not token:
            return False
        return True

    async def is_visible(self, request: Request) -> bool:
        return await self.is_accessible(request)

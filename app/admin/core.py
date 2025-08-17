# app/admin/core.py
from sqladmin import ModelView
from sqlalchemy.sql.sqltypes import Integer, String, Text
from sqlalchemy import inspect
from typing import Set, List, Any
from functools import cached_property
from sqlalchemy.orm import RelationshipProperty
from starlette.requests import Request


class AutoModelView(ModelView):
    """
    Автоматически формирует column_list из всех колонок модели,
    кроме исключённых. Работает корректно с sqladmin.
    """
    column_searchable_list = ['name', 'name_ru']
    # Поля, которые исключаем по умолчанию в таблице
    exclude_columns: Set[str] = {
        "password",
        "secret",
        "api_key",
        "token",
        "salt",
        "hashed_password",
        "created_at",
        "updated_at",
        "deleted_at",
        "is_deleted",
        "description",
        "id"
    }
    # поля, которые исключаем в форме
    form_excluded_columns = ['created_at', 'updated_at', 'pk']
    # порядок вывода колонок
    sort_columns: tuple[str] = ("primary_key", "index", "nullable",)
    type_priority: tuple[Any] = (String, Integer)
    type_excluded: tuple[Any] = (Text,)
    # Включать ли первичный ключ в список
    include_pk_in_list: bool = True

    @cached_property
    def _model_columns(self) -> List[Any]:
        """Возвращает список атрибутов модели для column_list."""
        mapper = inspect(self.model)
        columns: List[Any] = []
        tmp: dict = {}
        rel: List[Any] = []
        for attr in mapper.attrs:
            if (hasattr(attr, "columns") and attr.key not in self.exclude_columns):
                # Только колонки (не relationships)
                col = attr.columns[0]
                # Исключить типы self.type_excluded
                if type(getattr(col, 'type')) in self.type_excluded:
                    continue
                x = sum((False if getattr(col, key) is None
                        else getattr(col, key)) * 2 ** n
                        for n, key in enumerate(reversed(self.sort_columns))
                        )
                y = sum(isinstance(getattr(col, 'type'), a) * 2**n
                        for n, a in enumerate(reversed(self.type_priority)))
                tmp[attr.key] = (attr, x, y)
                # tmp.append((attr, x, y, attr.key))
            if isinstance(attr, RelationshipProperty):
                # relationships
                if (attr.direction.name == "MANYTOONE" and
                        attr.key not in self.exclude_columns):
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
        columns = [a for a, *b in reversed(sorted_columns)]
        # Добавляем превью изображения если модель поддерживает его
        if hasattr(self.model, 'image_path') and "image_preview" not in [getattr(c, 'key', str(c)) for c in columns]:
            columns.append("image_preview")

        return columns

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Устанавливаем column_list, если не задан явно
        if not cls.column_list:
            cls.column_list = cls._model_columns


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

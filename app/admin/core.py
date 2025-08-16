# app/admin/core.py
from sqladmin import ModelView
from sqlalchemy.sql.sqltypes import Integer, String, Text
from sqlalchemy import inspect
from typing import Set, List, Any
from functools import cached_property
from sqlalchemy.orm import RelationshipProperty


class AutoModelView(ModelView):
    """
    Автоматически формирует column_list из всех колонок модели,
    кроме исключённых. Работает корректно с sqladmin.
    """
    column_searchable_list = ['name', 'name_ru']
    # Поля, которые исключаем по умолчанию
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
        # pk_name = mapper.primary_key[0].name if mapper.primary_key else None
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
        return columns

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Устанавливаем column_list, если не задан явно
        if not cls.column_list:
            cls.column_list = cls._model_columns

# app/admin/core.py
# app/admin/sqladmin.py
from sqladmin import ModelView
from sqlalchemy.sql.sqltypes import Integer, String
from sqlalchemy import inspect
from typing import Set, List, Any
from functools import cached_property


class AutoModelView(ModelView):
    """
    Автоматически формирует column_list из всех колонок модели,
    кроме исключённых. Работает корректно с sqladmin.
    """
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
    # порядок вывода колонок
    sort_columns: tuple[str] = (
            "primary_key",
            "index",
            "nullable",
            # "type"
            )
    type_priority: tuple[Any] = (String, Integer)

    # Включать ли первичный ключ в список
    include_pk_in_list: bool = True

    @cached_property
    def _model_columns(self) -> List[Any]:
        """Возвращает список атрибутов модели для column_list."""
        mapper = inspect(self.model)
        # pk_name = mapper.primary_key[0].name if mapper.primary_key else None
        columns = []
        tmp = []
        for attr in mapper.attrs:
            # Только колонки (не relationships)
            """
            ttr.columns[0]=Column('count_drink',
            Integer(),
            table=<categories>,
            nullable=False,
            """
            if (hasattr(attr, "columns")
                    and attr.key not in self.exclude_columns):
                col = attr.columns[0]
                x = sum((False if getattr(col, key) is None
                        else getattr(col, key))*2**n
                        for n, key in enumerate(reversed(self.sort_columns)))
                y = sum(isinstance(getattr(col, 'type'), a) * 2**n
                        for n, a in enumerate(reversed(self.type_priority)))
                tmp.append((attr, x, y, attr.key))
        sorted_columns = sorted(tmp, key=lambda a: (a[1], a[2], a[3]))
        columns = [a for a, *b in reversed(sorted_columns)]
        return columns

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Устанавливаем column_list, если не задан явно
        if not cls.column_list:
            cls.column_list = cls._model_columns

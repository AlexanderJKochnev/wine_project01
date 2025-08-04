# app/core/schemas/base_schema.py

""" Base Pydantic Model """
from typing import NewType, Any
# from pydantic import BaseModel
from pydantic import BaseModel, create_model, ConfigDict
from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeMeta
# from typing import Type  # , get_args, get_origin
# from datetime import datetime

PyModel = NewType("PyModel", BaseModel)


class Base(BaseModel):
    class Config:
        from_attributes = True


def create_pydantic_model_from_orm(
    orm_model: DeclarativeMeta,
    model_name: str = "DynamicModel"
) -> type[BaseModel]:
    """
    Создаёт Pydantic-модель для создания объекта, исключая:
    - primary_key
    - поля с default/server_default
    Делает nullable-поля опциональными.
    """
    mapper = inspect(orm_model)
    fields = {}

    for column in mapper.columns:
        # Пропускаем автогенерируемые поля
        if (
            column.primary_key or
            column.default is not None or
            column.server_default is not None
        ):
            continue

        field_type = column.type.python_type
        field_name = column.name

        # Если поле может быть NULL, делаем Optional
        if column.nullable:
            fields[field_name] = (field_type | None, None)
        else:
            fields[field_name] = (field_type, ...)

    # Правильный способ: create_model
    return create_model(
        model_name,
        __config__=ConfigDict(from_attributes=True),
        **fields
    )


def get_pydantic_model_from_orm(
    orm_model: DeclarativeMeta,
    model_name: str = "DynamicModel"
) -> type[BaseModel]:
    """
    Создаёт Pydantic-модель для вывода объекта, исключая:
    - primary_key
    - поля с default/server_default
    Делает nullable-поля опциональными.
    """
    mapper = inspect(orm_model)
    fields = {}

    for column in mapper.columns:
        # Пропускаем автогенерируемые поля
        if (
            column.primary_key  # or
            # column.default is not None or
            # column.server_default is not None
        ):
            continue

        field_type = column.type.python_type
        field_name = column.name

        # Если поле может быть NULL, делаем Optional
        if column.nullable:
            fields[field_name] = (field_type | None, None)
        else:
            fields[field_name] = (field_type, ...)

    # Правильный способ: create_model
    return create_model(
        model_name,
        __config__=ConfigDict(from_attributes=True),
        **fields
    )


def create_pydantic_model_from_orm_rel(orm_model: DeclarativeMeta,
                                       model_name: str = None,
                                       include_relationships: bool = False,
                                       ) -> type[BaseModel]:
    """
    Создаёт Pydantic-модель для ORM-модели.

    :param orm_model: SQLAlchemy ORM модель
    :param model_name: имя Pydantic-модели
    :param include_relationships: включать ли отношения (по умолчанию — нет)
    :return: Pydantic-модель
    """
    model_name = model_name or f"{orm_model.__name__}Create"

    mapper = inspect(orm_model)
    fields = {}

    # 1. Обрабатываем колонки
    for column in mapper.columns:
        # Пропускаем primary_key, default, server_default
        if (column.primary_key or column.default is not None or column.server_default is not None):
            continue

        field_type = column.type.python_type
        field_name = column.name

        if column.nullable:
            fields[field_name] = (field_type | None, None)
        else:
            fields[field_name] = (field_type, ...)

    # 2. Обрабатываем relationships (опционально)
    if include_relationships:
        for rel_name, relationship_prop in mapper.relationships.items():
            # Проверяем, можно ли вставлять объект напрямую
            # Например, если это many-to-one и не "backref"
            if relationship_prop.uselist:
                # Списки (one-to-many) — как Optional[list]
                fields[rel_name] = (list[Any] | None, None)
            else:
                # Один объект (many-to-one) — Optional[dict] или None
                fields[rel_name] = (dict | None, None)

    # Создаём модель
    return create_model(model_name,
                        __config__=ConfigDict(from_attributes=True),
                        **fields
                        )

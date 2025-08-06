# app/core/schemas/base_schema.py

""" Base Pydantic Model """
from typing import NewType, Any, Dict, Type, List
# from pydantic import BaseModel
from pydantic import BaseModel, create_model, ConfigDict
from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeMeta
# from typing import Type  # , get_args, get_origin
# from datetime import datetime


PyModel = NewType("PyModel", BaseModel)

"""
class Base(BaseModel):
    class Config:
        from_attributes = True

"""


def create_pydantic_models_from_orm(
    orm_model: DeclarativeMeta,
    model_name: str = None,
    include_relationships: bool = False,
    id_field: str = "id",
) -> Dict[str, Type[BaseModel]]:
    """
    Генерирует полный набор Pydantic-схем для CRUD + List с пагинацией.
    """
    model_name = model_name or orm_model.__name__
    mapper = inspect(orm_model)

    # Поля, которые можно задавать вручную (без id, default, PK и т.п.)
    base_fields = {}
    for column in mapper.columns:
        if (
            column.primary_key or
            column.default is not None or
            column.server_default is not None
        ):
            continue
        field_type = column.type.python_type
        field_name = column.name
        base_fields[field_name] = (field_type | None, None) if column.nullable else (field_type, ...)

    # Отношения (опционально)
    rel_fields = {}

    if include_relationships:
        for rel_name, relationship_prop in mapper.relationships.items():
            rel_type = List[Any] | None if relationship_prop.uselist else (Dict | None)
            rel_type = str
            rel_fields[rel_name] = (rel_type, None)

    # --- Create ---
    CreateModel = create_model(
        f"{model_name}Create",
        __config__=ConfigDict(from_attributes=True),
        **{**base_fields, **rel_fields}
    )

    # --- Update ---
    UpdateModel = create_model(
        f"{model_name}Update",
        __config__=ConfigDict(from_attributes=True),
        **{k: (t, None) for k, (t, _) in {**base_fields, **rel_fields}.items()}
    )

    # --- Read ---
    read_fields = {id_field: (int, ...)}
    read_fields.update(base_fields)
    read_fields.update(rel_fields)
    ReadModel = create_model(
        f"{model_name}Read",
        __config__=ConfigDict(from_attributes=True),
        **read_fields
    )

    # --- Delete Response ---
    DeleteResponse = create_model(
        f"{model_name}Delete",
        __config__=ConfigDict(from_attributes=True),
        id=(int, ...),
        success=(bool, ...),
        message=(str, "Object deleted successfully")
    )

    # --- List Response (с пагинацией) ---
    ListModel = create_model(
        f"{model_name}List",
        __config__=ConfigDict(from_attributes=True),
        items=(List[ReadModel], ...),           # список объектов
        page=(int, ...),
        page_size=(int, ...),
        total=(int, ...),
        has_next=(bool, ...),
        has_prev=(bool, ...)
    )

    return {
        "Create": CreateModel,
        "Update": UpdateModel,
        "Read": ReadModel,
        "DeleteResponse": DeleteResponse,
        "List": ListModel
    }


def create_detail_view_model(
    orm_model: DeclarativeMeta,
    model_name: str = None,
    include_relationships: bool = True,
) -> type[BaseModel]:
    """
    Создаёт Pydantic-схему для детального просмотра:
    - Исключает: id, primary_key, foreign_keys
    - Включает: все обычные поля + поля из relationships (например, department.name)
    Пример: User → поля: name, email, department_name, profile_phone
    """
    model_name = model_name or orm_model.__name__
    mapper = orm_model.__mapper__
    fields = {}

    # 1. Обычные колонки (не PK, не FK)
    for column in mapper.columns:
        if column.primary_key or getattr(column, "foreign_keys", None):
            continue
        field_type = column.type.python_type
        field_name = column.name
        fields[field_name] = (field_type | None, None) if column.nullable else (field_type, ...)

    # 2. Поля из relationships
    if include_relationships:
        for rel_name, relationship in mapper.relationships.items():
            # if relationship.uselist:  # skip one-to-many
            #     continue

            remote_model = relationship.entity.entity
            remote_mapper = remote_model.__mapper__

            for col in remote_mapper.columns:
                if col.primary_key:
                    continue
                if not hasattr(col.type, "python_type"):
                    continue

                remote_field_name = col.name
                field_name = f"{rel_name}_{remote_field_name}"
                field_type = col.type.python_type

                # Например: department_name → str | None
                fields[field_name] = (field_type | None, None)
    return create_model(
        f"{model_name}DetailView",
        __config__=ConfigDict(from_attributes=True),
        **fields
    )

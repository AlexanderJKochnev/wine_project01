# app/core/schemas/base_schema.py

""" Base Pydantic Model """
from pydantic import BaseModel, create_model  # , model_validator, ConfigDict
from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeMeta, RelationshipProperty
from typing import NewType, Any, Dict, Type, List, Optional

PyModel = NewType("PyModel", BaseModel)


class Base(BaseModel):
    class Config:
        from_attributes = True


def create_pydantic_models_from_orm(
    orm_model: DeclarativeMeta,
    model_name: str = None,
    id_field: str = "id",
) -> Dict[str, type[BaseModel]]:
    """
    Генерирует Pydantic-схемы с автоматической поддержкой:
    - relationship-полей в формате: {rel_name}_{field}
    - например: department_name → берётся из user.department.name
    """
    model_name = model_name or orm_model.__name__
    mapper = inspect(orm_model)

    # Поля модели (без PK, default и т.п.)
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

    # Анализ relationships
    rel_fields = {}
    for rel_name, relationship in mapper.relationships.items():
        if relationship.uselist:  # skip one-to-many
            continue

        remote_model = relationship.entity.entity
        remote_mapper = remote_model.__mapper__

        for col in remote_mapper.columns:
            if col.primary_key or not hasattr(col.type, "python_type"):
                continue
            field_type = col.type.python_type
            virtual_field = f"{rel_name}_{col.name}"
            rel_fields[virtual_field] = (field_type | None, None)

    # --- Read Schema: включает relationship-поля ---
    read_fields = {
        id_field: (int, ...)
    }
    read_fields.update(base_fields)
    read_fields.update(rel_fields)

    def get_model_dump(self):
        data = {}
        # Основные поля
        for field_name in base_fields:
            data[field_name] = getattr(self, field_name, None)

        # Relationship-поля
        for virtual_field in rel_fields:
            parts = virtual_field.split("_", 1)
            if len(parts) != 2:
                continue
            rel_name, remote_field = parts
            rel_obj = getattr(self, rel_name, None)
            if rel_obj is not None:
                data[virtual_field] = getattr(rel_obj, remote_field, None)
            else:
                data[virtual_field] = None

        return data

    # Создаём ReadModel с кастомным model_dump
    ReadModel = create_model(
        f"{model_name}Read",
        __config__=type('Config', (), {'from_attributes': True}),
        model_dump=get_model_dump,
        **read_fields
    )

    # --- Остальные схемы (Create, Update, List, Delete) ---
    CreateModel = create_model(
        f"{model_name}Create",
        __config__=type('Config', (), {'from_attributes': True}),
        **base_fields
    )

    UpdateModel = create_model(
        f"{model_name}Update",
        __config__=type('Config', (), {'from_attributes': True}),
        **{k: (t, None) for k, (t, _) in base_fields.items()}
    )

    ListModel = create_model(
        f"{model_name}List",
        __config__=type('Config', (), {'from_attributes': True}),
        items=(List[ReadModel], ...),
        page=(int, ...),
        page_size=(int, ...),
        total=(int, ...),
        has_next=(bool, ...),
        has_prev=(bool, ...)
    )

    DeleteResponse = create_model(
        f"{model_name}Delete",
        __config__=type('Config', (), {'from_attributes': True}),
        id=(int, ...),
        success=(bool, ...),
        message=(str, "Object deleted successfully")
    )

    return {
        "Create": CreateModel,
        "Update": UpdateModel,
        "Read": ReadModel,
        "List": ListModel,
        "DeleteResponse": DeleteResponse
    }

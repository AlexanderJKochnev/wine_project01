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


class Base(BaseModel):
    class Config:
        from_attributes = True


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

    def to_dict(self) -> dict:
        """Возвращает словарь: {имя_поля: значение}"""
        return self.model_dump()

    ReadModel = create_model(
        f"{model_name}Read",
        __config__=ConfigDict(from_attributes=True),
        to_dict=to_dict,  # добавляем метод
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

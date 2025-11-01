# app/core/utils/pydantic_utils.py
# from pydantic import create_model, BaseModel
from decimal import Decimal
from typing import List, Optional, Type, Union

from pydantic import BaseModel, create_model
from sqlalchemy import Float, inspect, Integer, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql.type_api import TypeEngine
from app.core.schemas.base import PaginatedResponse, PYDANTIC_MODELS, PyModel
from app.core.repositories.sqlalchemy_repository import RepositoryMeta
from app.core.services.service import ServiceMeta


def get_service(model: Union[Type[DeclarativeBase], str]):
    """
    получение service layer по имени
    :param model: модель / имя модели
    """
    if not isinstance(model, str):
        model = model.__name__
    return ServiceMeta._registry.get(f'{model}'.lower(), None)
    # return ServiceRegistry.get(f'{model}'.lower())

def get_repo(model: Union[Type[DeclarativeBase], str]):
    """
    получение репозитория по имени
    :param model: модель / имя модели
    """
    if not isinstance(model, str):
        model = model.__name__
    return RepositoryMeta._registry.get(f'{model}'.lower(), None)
    # print(result, result.__name__, model)
    # return result


def get_pyschema(name: str, default: str = 'ReadSchema') -> PyModel:
    """
        получение pydantic schema по ее имени:
        name: имя схемы
        default: дефолтное имя (не у всех схем есть кастомизированные схемы, в этом случае берем базовую
    """
    def_schema = None
    for schema in PYDANTIC_MODELS:
        if schema.__name__.lower() == name.lower():
            return schema
        if schema.__name__.lower() == default.lower():
            def_schema = schema
            print('========', name)
    return def_schema


def pyschema_helper(model: Type[DeclarativeBase], schema_type: str, lang: str = None) -> PyModel:
    """
    по лучение py схемы для alchemy model по назначению (schema_type)
    :param model:
    :param schema_type:
    """
    name: str = model.__name__
    schema_types: dict = {'list': 'ListView',
                          'single': 'DetailView',
                          'read': 'Read',
                          'create': 'Create',
                          'update': 'Update',
                          'create_relation': 'CreateRelation',
                          'read_relation': 'ReadRelation'
                          }
    default: str = f'{schema_types.get(schema_type)}'
    if lang:
        default: str = f'{default}{lang.capitalize()}'
    pyname: str = f'{name}{default}'
    return get_pyschema(pyname, default)


def sqlalchemy_to_pydantic_post(
        model: Type[DeclarativeBase], *, exclude_fields: Optional[set] = None,
        optional_fields: Optional[set] = None, ) -> Type[BaseModel]:
    """
    Генерирует Pydantic модель для POST-запроса из SQLAlchemy 2+ модели.
    использование CategoryCreate = sqlalchemy_to_pydantic_post(Category)
    :param model: SQLAlchemy модель
    :param exclude_fields: Поля, которые нужно исключить (например, {'id', 'created_at'})
    :param optional_fields: Поля, которые должны быть Optional (даже если nullable=False)
    :return: Pydantic BaseModel класс
    """
    if exclude_fields is None:
        # Исключаем типичные служебные поля по умолчанию
        exclude_fields = {"id", "created_at", "updated_at"}

    if optional_fields is None:
        optional_fields = set()

    mapper = inspect(model)
    fields = {}

    for column in mapper.columns:
        if column.key in exclude_fields:
            continue

        # Определяем тип Python из типа SQLAlchemy
        python_type = _get_python_type(column.type)

        # Определяем, является ли поле обязательным
        is_required = not column.nullable and column.key not in optional_fields

        # Для Foreign Key - всегда int (ID связанной сущности)
        if hasattr(column, 'foreign_keys') and column.foreign_keys:
            python_type = int
            # Foreign Key обычно nullable=False, но может быть и nullable=True
            is_required = not column.nullable and column.key not in optional_fields

        # Если поле не обязательное - делаем его Optional
        if not is_required:
            from typing import Optional as TypingOptional
            python_type = TypingOptional[python_type]

        # Устанавливаем значение по умолчанию для необязательных полей
        default = ... if is_required else None

        fields[column.key] = (python_type, default)

    # Создаём Pydantic модель
    model_name = f"{model.__name__}Create"
    pydantic_model = create_model(model_name, **fields)

    return pydantic_model


def _get_python_type(sql_type: TypeEngine) -> type:
    """Преобразует SQLAlchemy тип в Python тип для Pydantic"""
    # Строковые типы
    if isinstance(sql_type, (String, Text)):
        return str

    # Целые числа
    if isinstance(sql_type, Integer):
        return int

    # Вещественные числа
    if isinstance(sql_type, Float):
        return float

    # Decimal (деньги, проценты и т.д.)
    if isinstance(sql_type, Numeric):
        return Decimal

    # По умолчанию - str (на случай неизвестных типов)
    return str


class PyUtils:

    @classmethod
    def read_response(cls, read_schema: Type[BaseModel]) -> Type[BaseModel]:
        return create_model(f'{read_schema.__name__}Response', __base__=read_schema)

    @classmethod
    def paginated_response(cls, schema: Type[BaseModel]) -> Type[PaginatedResponse]:
        return create_model(f"Paginated{schema.__name__}",
                            __base__=PaginatedResponse[schema])

    @classmethod
    def non_paginated_response(cls, schema: Type[BaseModel]) -> Type[List]:
        return create_model(f'NonPaginated{schema.__name__}',
                            __base__=List[schema])

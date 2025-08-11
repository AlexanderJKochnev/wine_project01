# app/core/schemas/base.py
"""
Базовые Pydantic схемы для валидации данных (включают поля из app/core/models/base_model/Base
"""
from typing import NewType, Generic, TypeVar, List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

PyModel = NewType("PyModel", BaseModel)
T = TypeVar("T")


class ShortSchema(BaseModel):
    """
        поля для представления во вложенных схемах
        ...языковой модуль
    """
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    name: str
    name_ru: Optional[str] = None


class BaseSchema(ShortSchema):
    """
    стандартные поля для read/create
    """
    model_config = ConfigDict(from_attributes=True,
                              arbitrary_types_allowed=True,
                              exclude_none=True)
    description: Optional[str] = None
    decsription_ru: Optional[str] = None

    def __init__(self, *args, **kwargs):
        pass


class FullSchema(BaseSchema):
    """
        все стандартные поля
    """
    id: int
    created_at: datetime
    updated_at: datetime


class UpdateSchema(BaseSchema):
    """
        все поля редактируемые
    """
    name: Optional[str] = None


class ListResponse(BaseModel, Generic[T]):
    items: List[T]
    total: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None
    has_next: Optional[int] = None
    has_prev: Optional[int] = None


class PaginatedResponse(ListResponse[T]):
    pass


class DeleteResponse(BaseModel):
    success: bool
    deleted_count: int = 1
    message: str

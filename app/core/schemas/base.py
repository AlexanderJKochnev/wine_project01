# app/core/schemas/base.py

from typing import NewType, Generic, TypeVar, List, Optional
from pydantic import BaseModel, ConfigDict


PyModel = NewType("PyModel", BaseModel)
T = TypeVar("T")


class BaseSchema(BaseModel):
    model_config = ConfigDict(rom_attributes=True,
                              arbitrary_types_allowed=True)


""" Общие для всех схем ответы. используются в роутерах """


class ListResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: Optional[int] = None
    page_size: Optional[int] = None
    total: Optional[int] = None
    has_next: Optional[int] = None
    has_prev: Optional[int] = None


class PaginatedResponse(ListResponse[T]):
    pass


class DeleteResponse(BaseModel):
    success: bool
    deleted_count: int = 1
    message: str

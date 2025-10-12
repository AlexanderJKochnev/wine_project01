# app/core/utils/pydantic_utils.py
from pydantic import create_model, BaseModel
from typing import Type, List
from app.core.schemas.base import PaginatedResponse


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

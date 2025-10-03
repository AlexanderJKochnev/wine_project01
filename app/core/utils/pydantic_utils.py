# app/core/utils/pydantic_utils.py
from pydantic import create_model, BaseModel
from typing import Type
from app.core.schemas.base import PaginatedResponse



class PyUtils:

    @classmethod
    def response_model(cls, read_schema: Type[BaseModel]) -> Type[BaseModel]:
        return create_model(f'{read_schema.__name__}Response', __base__=read_schema)

    @classmethod
    def paginated_response(cls, schema: Type[BaseModel]) -> Type[PaginatedResponse]:
        return create_model(f"Paginated{schema.__name__}",
                                               __base__=PaginatedResponse[schema])

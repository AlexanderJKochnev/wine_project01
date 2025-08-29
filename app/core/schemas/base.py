# app/core/schemas/base.py
"""
Базовые Pydantic схемы для валидации данных (включают поля из app/core/models/base_model/Base
"""
from typing import NewType, Generic, TypeVar, List, Optional, Any
from pydantic import BaseModel, ConfigDict, model_validator
from datetime import datetime

PyModel = NewType("PyModel", BaseModel)
T = TypeVar("T")


class PkSchema(BaseModel):
    id: int


class UniqueSchema(BaseModel):
    name: str


class ShortSchema(UniqueSchema):
    """
        поля для представления во вложенных схемах
        ...языковой модуль
    """
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class LangSchema(BaseModel):
    """ добавлять поля на других языках """
    name_ru: Optional[str] = None


class DescriptionSchema(BaseModel):
    """ добавлять поля описаний на других языках """
    description: Optional[str] = None
    description_ru: Optional[str] = None


class DateSchema(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ReadSchema(ShortSchema, LangSchema, DescriptionSchema, PkSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class ReadSchemaWithRealtionships(ReadSchema):
    model_config = ConfigDict(from_attributes=True,
                              arbitrary_types_allowed=True,
                              extr='allow',
                              populate_by_name=True,
                              exclude_none=True)

    @model_validator(mode='before')
    @classmethod
    def flatten_relationships(cls, data: Any):
        """
            Принимает ORM-объект, возвращает словарь с плоскими значениями.
            Никакой модификации исходного объекта!
        """
        if hasattr(data, '__dict__') or hasattr(data, '__class__'):
            # Это ORM-объект
            result = {}
            for field_name in cls.model_fields:
                if field_name == 'region' and hasattr(data, 'region') and data.region is not None:
                    result['region'] = data.region.name
                elif field_name == 'country' and hasattr(data, 'region') and data.region is not None:
                    result['country'] = data.region.country.name if data.region.country else None
                else:
                    value = getattr(data, field_name, None)
                    # Обычные связанные объекты (category, food и т.д.)
                    if hasattr(value, '_sa_instance_state') and hasattr(value, 'name'):
                        result[field_name] = value.name
                    else:
                        result[field_name] = value
            return result
            """
                value = getattr(data, key, None)
                if value is None:
                    result[key] = None
                elif hasattr(value, '_sa_instance_state'):
                    # Это ORM-объект (не примитив) → извлекаем .name
                    if hasattr(value, 'name'):
                        result[key] = value.name
                    elif key == 'region' and hasattr(value, 'country'):
                        country_name = value.country.name if value.country else ""
                        result[key] = f"{value.name} - {country_name}".strip(" - ")
                    else:
                        result[key] = str(value)
                else:
                    # Простое значение (int, str, bool и т.д.)
                    result[key] = value
            return result

            """
class CreateSchema(UniqueSchema, LangSchema, DescriptionSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class UpdateSchema(ShortSchema, LangSchema, DescriptionSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    name: Optional[str] = None


class FullSchema(ReadSchema, DateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


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


class ImageMixin:
    image_url: Optional[str] = None  # Добавляем поле для URL изображения

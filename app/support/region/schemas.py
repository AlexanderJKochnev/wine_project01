# app/support/region/schemas.py

from typing import Any, Optional

from pydantic import computed_field, ConfigDict, Field, model_validator

from app.core.schemas.base import (CreateSchema, DateSchema, PkSchema, ReadSchema, ShortSchema, UpdateSchema)
from app.support.country.schemas import CountryShort


class CustomSchema:
    country: Optional[CountryShort] = None


class CustomCreateSchema:
    country_id: int = Field(..., description="ID страны (Country.id) для связи Many-to-One")


class CustomUpdSchema:
    country_id: Optional[int] = None


class RegionShort(ShortSchema, CustomSchema):
    pass


class RegionRead(ReadSchema):
    model_config = ConfigDict(from_attributes=True,
                              arbitrary_types_allowed=True,
                              # protected_namespaces=('_',),
                              extr='allow',
                              populate_by_name=True,
                              exclude_none=True)

    # country: Optional[CountryShort] = None
    country: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def flatten_relationships(cls, data: Any):
        """
        Преобразуем связанные объекты в строки ДО валидации.
        """
        """
                Принимает ORM-объект, возвращает словарь с плоскими значениями.
                Никакой модификации исходного объекта!
                """
        if hasattr(data, '__dict__') or hasattr(data, '__class__'):
            # Это ORM-объект
            result = {}
            for key in cls.model_fields:
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
    @computed_field
    @property
    def country_str(self) -> Optional[str]:
        return self.country.model_dump().get('name') if self.country else None

    def model_dump(self, **kwargs) -> dict[Any]:
        result = super().model_dump(**kwargs)
        result.pop('country')
        result['country'] = result.pop('country1', None)
        return result
    """

class RegionCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)
    # country_id: int = Field(..., description="ID страны (Country.id) для связи Many-to-One")


class RegionUpdate(UpdateSchema, CustomUpdSchema):
    pass


class RegionCreateResponseSchema(RegionCreate, PkSchema, DateSchema):
    pass

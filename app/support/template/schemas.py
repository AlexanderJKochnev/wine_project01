# app/support/template/schemas.py

"""
Custom - нестандартные поля характерные для этой формы. Если их нет - оставить pass.
         модель полностью не удалять.
Short - короткая форма которая будет отражаться в связанном поле связанной таблицы
Read - модель для чтения - все поля кроме id, created_at, updated_at
Create - поля котоые должны и могут быть заполнены для записи в базу данных.
    При отсутсвии обязательных данных будеит выдана ошибка
Update - все поля как и в Create, НО ЗАПОЛНЯТЬ НУЖНО ТОЛЬКО ТЕ ПОЛЯ КОТОРЫЕ МЕНЯЮТСЯ
Full - все поля включая системные и скрытые
"""

# app/support/region/schemas.py

from typing import Optional

from pydantic import ConfigDict, Field

from app.core.schemas.base import (CreateSchema, PkSchema, ReadSchema,
                                   ShortSchema, UpdateSchema, DateSchema)
from app.support.country.schemas import CountryShort


class CustomSchema:
    country: CountryShort


class CustomCreateSchema:
    country_id: int = Field(..., description="ID страны (Country.id) для связи Many-to-One")


class CustomUpdSchema:
    country_id: Optional[int] = None


class TemplateShort(ShortSchema, CustomSchema):
    pass


class TemplateRead(ReadSchema, CustomSchema):
    model_config = ConfigDict(from_attributes=True,
                              arbitrary_types_allowed=True,
                              # populate_by_name=True,
                              )  # , exclude_none=True)


"""    def dict(self, **kwargs):
        # Переопределяем dict() чтобы получить плоскую структуру
        result = super().dict(**kwargs)
        for key, val in result.items():
            if not isinstance(val, dict):
                continue
            val = 'тест'
"""


class TemplateCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)
    # country_id: int = Field(..., description="ID страны (Country.id) для связи Many-to-One")


class TemplateUpdate(UpdateSchema, CustomUpdSchema):
    pass


class TemplateCreateResponseSchema(TemplateCreate, PkSchema, DateSchema):
    pass

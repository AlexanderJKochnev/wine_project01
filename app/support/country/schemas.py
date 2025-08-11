# app/support/country/schemas.py
"""
    После замен как указано в главной инструкции сделай следующее:
    1.

"""


from app.core.schemas.base import BaseSchema, FullSchema, UpdateSchema, ShortSchema
from app.support.category.schemas import CategoryShort
from pydantic import ConfigDict

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


class CountryCustom:
    category_id: int


class CountryShort(ShortSchema):
    pass


class CountryRead(BaseSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)
    category: CategoryShort


class CountryCreate(BaseSchema, CountryCustom):
    pass


class CountryUpdate(UpdateSchema, CountryCustom):
    pass


class CountryFull(FullSchema, CountryCustom):
    pass

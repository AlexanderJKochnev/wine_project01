# app/support/item/schemas.py

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


class ItemCustom:
    # drink_id: int
    pass


class ItemShort(ShortSchema):
    pass


class ItemRead(BaseSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)
    category: CategoryShort


class ItemCreate(BaseSchema, ItemCustom):
    pass


class ItemUpdate(UpdateSchema, ItemCustom):
    pass


class ItemFull(FullSchema, ItemCustom):
    pass

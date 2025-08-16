# app/support/warehouse/schemas.py
from app.core.schemas.base import BaseSchema, FullSchema, UpdateSchema, ShortSchema
from app.support.customer.schemas import CustomerShort
from pydantic import ConfigDict
from typing import Optional

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


class WarehouseCustom:
    customer_id: Optional[int]
    address: Optional[str]


class WarehouseShort(ShortSchema):
    pass


class WarehouseRead(BaseSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)
    customer: CustomerShort


class WarehouseCreate(BaseSchema, WarehouseCustom):
    pass


class WarehouseUpdate(UpdateSchema, WarehouseCustom):
    pass


class WarehouseFull(FullSchema, WarehouseCustom):
    pass

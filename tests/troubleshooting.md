Распространенные ошибки
1. <Response [409 Conflict]>: в схеме Create стоят автоинкрементные поля (id, pk) убрать
2. <Response [422 Unprocessable Entity]> AssertionError: 
   1. получение записи: в схеме Read отсутствует id, добавить
   2. Порядок роутеров - сначала статические затем динамические
3. Error extracting attribute: MissingGreenlet: 
   1. в model.py добавить
      1. from __future__ import annotations
      2. from typing import TYPE_CHECKING
      3. if TYPE_CHECKING:  # parent model of relationship
             from app.support.customer.model import Customer
      4. lazy="selectin" так как ниже:
         1. customer: Mapped["Customer"] = relationship(back_populates="warehouses", lazy="selectin")
   2. в repository.py добавить def get_query(self) со следующим содержимым: 
      1. return select(Warehouse).options(joinedload(Warehouse.customer))
   3. в schemas.py
      1. схему ..Read унаследовать от ReadSchemaWithRealtionships
      2. поле relationships обозначить как Optional[str] = None
4. ddd
5. 
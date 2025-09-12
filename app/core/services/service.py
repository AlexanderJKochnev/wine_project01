# app.core.service/service_layer.py

from typing import Any, Dict, List, Optional, TypeVar

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta, Session

from app.core.models.base_model import Base
from app.core.repositories.sqlalchemy_repository import Repository
from app.core.schemas.base import DeleteResponse
from app.core.utils.common_utils import get_all_dict_paths, get_nested, set_nested, pop_nested

ModelType = TypeVar("ModelType", bound=DeclarativeMeta)


class Service:
    def __init__(self, repositiory: Repository, model: Base):
        self.repository = repositiory
        # self.model = model

    def get_models(self) -> List[ModelType]:
        return (cls for cls in Base.registry._class_registry.values() if
                isinstance(cls, type) and hasattr(cls, '__table__'))

    def get_model_by_name(self, name: str) -> ModelType:
        for mode in self.get_models():
            if any((mode.__name__.lower() == name, mode.__tablename__.lower() == name)):
                return mode

    async def create(self, data: ModelType, model: ModelType, session: AsyncSession) -> ModelType:
        """ create & return record """
        # удаляет пустые поля
        data_dict = data.model_dump(exclude_unset=True)
        obj = model(**data_dict)
        result = await self.repository.create(obj, model, session)
        # тут можно добавить преобразования результата потом commit в роутере
        return result

    async def get_or_create(self, data: ModelType, model: ModelType, session: Session) -> ModelType:
        """ использовать вместо create """

        data_dict = data.model_dump(exclude_unset=True)

        result = await self.repository.get_by_obj(data_dict, model, session)
        if result:
            return result
        else:
            obj = model(**data_dict)

            result = await self.repository.create(obj, model, session)
            # тут можно добавить преобразования результата потом commit в роутере
            return result

    async def update_or_create(self,
                               lookup: Dict[str, Any],
                               defaults: Dict[str, Any],
                               model: ModelType,
                               session: Session) -> ModelType:
        """ ищет запись по lookup и обновляет значениями default,
            если не находит - создает со значениями lookup + default
            замена patch? - нужно сделать схемы
        """
        result = await self.repository.get_by_obj(lookup, model, session)
        if result:
            id = result['id']
            return await self.repository.patch(id, defaults, model, session)
        else:
            data = {**lookup, **defaults}
            obj = model(**data)
            return await self.repository.create(obj, model, session)

    async def create_relation(self, data: ModelType, model: ModelType, session: AsyncSession) -> ModelType:
        """ create & return record with all relations"""
        try:
            # 0. вложенный словарь с данными в осноновной и связаных моделях
            # 1. получаем словарь: {путь к значениям: model} для вложенны сущностей
            main_dict = {key: self.get_model_by_name(val) for key, val in get_all_dict_paths(data).items()}
            # 2. если пустой пропускаем следующее:
            if main_dict:       # обрабатываем все что глубже, начиная снизу
                for key, val in main_dict.items():
                    subdata = pop_nested(data, key)
                    # _ = val(**subdata)  # data validation
                    obj = self.get_or_create(subdata, val, session)
                    if obj.get('id'):
                        set_nested(data, f'{key}_id', obj.get('id'))
            obj = await self.create(data, model, session)
            return obj
        except Exception as e:
            return e

    async def get_by_id(self, id: int, model: ModelType, session: AsyncSession) -> Optional[ModelType]:
        """
        get one record by id
        """
        obj = await self.repository.get_by_id(id, model, session)
        return obj

    async def get_all(self, page: int, page_size: int, model: ModelType, session: AsyncSession, ) -> List[dict]:
        # Запрос с загрузкой связей и пагинацией
        skip = (page - 1) * page_size
        items, total = await self.repository.get_all(skip, page_size, model, session)
        result = {"items": items,
                  "total": total,
                  "page": page,
                  "page_size": page_size,
                  "has_next": skip + len(items) < total,
                  "has_prev": page > 1}
        return result

    async def patch(self, id: Any, data: ModelType, model: ModelType, session: AsyncSession) -> Optional[ModelType]:
        data_dict = data.model_dump(exclude_unset=True)
        obj = await self.repository.patch(id, data_dict, model, session)
        return obj

    async def delete(self, obj: ModelType, model: ModelType, session: AsyncSession) -> bool:
        result = await self.repository.delete(obj, session)
        return result

# -------------------
    async def search_in_main_table(self,
                                   query: str,
                                   page: int,
                                   page_size: int,
                                   model: ModelType,
                                   session: AsyncSession) -> List[Any]:
        skip = (page - 1) * page_size
        return await self.repository.search_in_main_table(query, page, page_size, skip, model, session)

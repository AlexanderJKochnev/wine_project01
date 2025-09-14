# app.core.service/service_layer.py

from typing import Any, Dict, List, Optional, Type

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.models.base_model import Base
from app.core.utils.alchemy_utils import get_models
from app.core.repositories.sqlalchemy_repository import ModelType, Repository
from app.core.utils.common_utils import get_all_dict_paths, pop_nested, set_nested


class Service:

    @classmethod
    def get_model_by_name(cls, name: str) -> ModelType:
        for mode in get_models():
            if any((mode.__name__.lower() == name, mode.__tablename__.lower() == name)):
                return mode

    @classmethod
    async def create(cls, data: ModelType, repository: Type[Repository], model: ModelType,
                     session: AsyncSession) -> ModelType:
        """ create & return record """
        # удаляет пустые поля
        data_dict = data.model_dump(exclude_unset=True)
        obj = model(**data_dict)
        result = await repository.create(obj, model, session)
        # тут можно добавить преобразования результата потом commit в роутере
        return result

    async def get_or_create(cls, data: ModelType, repository: Type[Repository],
                            model: ModelType, session: Session) -> ModelType:
        """ использовать вместо create """

        data_dict = data.model_dump(exclude_unset=True)

        result = await repository.get_by_obj(data_dict, model, session)
        if result:
            return result
        else:
            obj = model(**data_dict)

            result = await repository.create(obj, model, session)
            # тут можно добавить преобразования результата потом commit в роутере
            return result

    async def update_or_create(cls,
                               lookup: Dict[str, Any],
                               defaults: Dict[str, Any],
                               repository: Type[Repository], model: ModelType,
                               session: Session) -> ModelType:
        """ ищет запись по lookup и обновляет значениями default,
            если не находит - создает со значениями lookup + default
            замена patch? - нужно сделать схемы
        """
        result = await repository.get_by_obj(lookup, model, session)
        if result:
            id = result['id']
            return await repository.patch(id, defaults, model, session)
        else:
            data = {**lookup, **defaults}
            obj = model(**data)
            return await cls.repository.create(obj, model, session)

    async def create_relation(cls, data: ModelType, repository: Type[Repository],
                              model: ModelType, session: AsyncSession) -> ModelType:
        """ create & return record with all relations"""
        try:
            # 0. вложенный словарь с данными в осноновной и связаных моделях
            # 1. получаем словарь: {путь к значениям: model} для вложенны сущностей
            main_dict = {key: cls.get_model_by_name(val) for key, val in get_all_dict_paths(data).items()}
            # 2. если пустой пропускаем следующее:
            if main_dict:       # обрабатываем все что глубже, начиная снизу
                for key, val in main_dict.items():
                    subdata = pop_nested(data, key)
                    # _ = val(**subdata)  # data validation
                    obj = cls.get_or_create(subdata, val, session)
                    if obj.get('id'):
                        set_nested(data, f'{key}_id', obj.get('id'))
            obj = await cls.create(data, model, session)
            return obj
        except Exception as e:
            return e

    async def get_by_id(cls, id: int, repository: Type[Repository], model: ModelType,
                        session: AsyncSession) -> Optional[ModelType]:
        """
        get one record by id
        """
        try:
            return await repository.get_by_id(id, model, session)
        except Exception:
            # logger.error(f"Error in get_by_id: {e}")
            raise

    async def get_all(cls, page: int, page_size: int, repository: Type[Repository], model: ModelType,
                      session: AsyncSession, ) -> List[dict]:
        # Запрос с загрузкой связей и пагинацией
        skip = (page - 1) * page_size
        items, total = await repository.get_all(skip, page_size, model, session)
        result = {"items": items,
                  "total": total,
                  "page": page,
                  "page_size": page_size,
                  "has_next": skip + len(items) < total,
                  "has_prev": page > 1}
        return result

    async def patch(cls, obj: ModelType, data: ModelType, repository: Type[Repository], session: AsyncSession) -> (
            Optional)[ModelType]:
        data_dict = data.model_dump(exclude_unset=True)
        obj = await repository.patch(obj, data_dict, session)
        return obj

    async def delete(cls, obj: ModelType, repository: Type[Repository],
                     session: AsyncSession) -> bool:
        result = await repository.delete(obj, session)
        return result

# -------------------
    async def search_in_main_table(cls,
                                   query: str,
                                   page: int,
                                   page_size: int,
                                   repository: Type[Repository], model: ModelType,
                                   session: AsyncSession) -> List[Any]:
        skip = (page - 1) * page_size
        return await repository.search_in_main_table(query, page, page_size, skip, model, session)

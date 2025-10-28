# app.core.service/service.py

from datetime import datetime
from typing import Any, Dict, List, Optional, Type

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.repositories.sqlalchemy_repository import ModelType, Repository
from app.core.utils.alchemy_utils import get_models, parse_unique_violation2

joint = '. '


class Service:
    """
    проверить ВОТ ВСЕХ МЕТОДАХ можно использщовать базовый репо.
    """
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
        return result

    @classmethod
    async def get_or_create(cls, data: ModelType, repository: Type[Repository],
                            model: ModelType, session: Session) -> ModelType:
        """ использовать вместо create """
        try:
            data_dict = data.model_dump(exclude_unset=True)
            # поиск существующей записи по полному совпадению объектов
            instance = await repository.get_by_fields(data_dict, model, session)
            if instance:
                return instance
            # запись не найдна
            obj = model(**data_dict)
            instance = await repository.create(obj, model, session)
            await session.flush()
            await session.refresh(instance)
            if not instance.id:
                # Если ID все еще None, принудительно коммитим и снова обновляем
                await session.commit()
                await session.refresh(instance)
            return instance
        except IntegrityError as e:
            # поиск по объекту не всегда дает верный результат
            # - могут быть отклонения в необязательных полях ("Превосходный" != "превосходный")
            # -при полном совпадении обязательных, что выбросит ошибку "нарушение уникальности"
            error_msg = str(e)
            await session.rollback()
            filter = parse_unique_violation2(error_msg)  # ищем какие ключи дали нарушение уникальности
            if filter:  # есть поля по которым нарушена интеграция
                # еще раз ищем запись
                existing_instance = await repository.get_by_fields(filter, model, session)
                if existing_instance:   # запись найдена
                    return existing_instance
                else:   # запись не найден и не может быть добавлена
                    raise Exception("запись не может быть добавлена по неивестной причине")
        except Exception as e:
            raise Exception(f"UNKNOWN_ERROR: {str(e)}") from e

    @classmethod
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

    @classmethod
    async def create_relation(cls, data: ModelType,
                              repository: Type[Repository], model: ModelType, session: Session) -> ModelType:
        """
        создание записей из json - со связями
        """

        data_dict = data.model_dump(exclude_unset=True)
        result = await repository.get_by_obj(data_dict, model, session)
        if result:
            return result
        else:
            obj = model(**data_dict)

            result = await repository.create(obj, model, session)
            # тут можно добавить преобразования результата потом commit в роутере
            return result

    @classmethod
    async def get_by_id(cls, id: int, repository: Type[Repository], model: ModelType,
                        session: AsyncSession) -> Optional[ModelType]:
        """
        get one record by id
        """
        result = await repository.get_by_id(id, model, session)
        return result

    @classmethod
    async def get_all(cls, ater_date: datetime,
                      page: int, page_size: int, repository: Type[Repository], model: ModelType,
                      session: AsyncSession, ) -> List[dict]:
        # Запрос с загрузкой связей и пагинацией
        skip = (page - 1) * page_size
        items, total = await repository.get_all(ater_date, skip, page_size, model, session)
        result = {"items": items,
                  "total": total,
                  "page": page,
                  "page_size": page_size,
                  "has_next": skip + len(items) < total,
                  "has_prev": page > 1}
        return result

    @classmethod
    async def get(cls, after_date: datetime,
                  repository: Type[Repository], model: ModelType,
                  session: AsyncSession,) -> Optional[List[ModelType]]:
        # Запрос с загрузкой связей -  возвращает список
        result = await repository.get(after_date, model, session)
        return result

    @classmethod
    async def patch(cls, obj: ModelType, data: ModelType, repository: Type[Repository], session: AsyncSession) -> (
            Optional)[ModelType]:
        data_dict = data.model_dump(exclude_unset=True)
        obj = await repository.patch(obj, data_dict, session)
        return obj

    @classmethod
    async def delete(cls, obj: ModelType, repository: Type[Repository],
                     session: AsyncSession) -> bool:
        result = await repository.delete(obj, session)
        return result

    @classmethod
    async def search(cls,
                     repository: Type[Repository],
                     model: ModelType,
                     session: AsyncSession,
                     **kwargs) -> List[ModelType]:
        paging = False
        if not kwargs:
            kwargs: dict = {}
        else:
            if kwargs.get('page') and kwargs.get('page_size'):
                limit = kwargs.pop('page_size')
                skip = (kwargs.pop('page') - 1) * limit
                kwargs['limit'], kwargs['skip'] = limit, skip
                paging = True
        items, total = await repository.search(model, session, **kwargs)
        # items, total = await repository.search_in_main_table(filter, model, session, skip, page_size)
        if paging:
            result = {"items": items,
                      "total": total,
                      "page": skip,
                      "page_size": limit,
                      "has_next": skip + len(items) < total,
                      "has_prev": skip > 1}
        else:
            result = items
        return result

    @classmethod
    async def search_all(cls,
                         filter: str,
                         repository: Type[Repository],
                         model: ModelType,
                         session: AsyncSession,
                         **kwargs) -> List[ModelType]:
        items, _ = await repository.search(model, session, **kwargs)
        return items

    @classmethod
    async def get_list_view_page(cls, page: int, page_size: int,
                                 repository: Type[Repository], model: ModelType, session: AsyncSession, ) -> List[dict]:
        # Запрос с загрузкой связей и пагинацией
        skip = (page - 1) * page_size
        rows, total = await repository.get_list_view_page(skip, page_size, model, session)
        result = {"rows": rows,
                  "total": total,
                  "page": page,
                  "page_size": page_size,
                  "has_next": skip + len(rows) < total,
                  "has_prev": page > 1}
        return result

    @classmethod
    async def get_list_view(cls, repository: Type[Repository],
                            model: ModelType, session: AsyncSession, ) -> List[tuple]:
        # Запрос с загрузкой связей и пагинацией
        rows = await repository.get_list_view(model, session)
        return rows

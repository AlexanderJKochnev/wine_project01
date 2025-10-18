# app/core/repositories/sqlalchemy_repository.py
""" не использовать Depends в этом контексте, он не входит в FastApi - только в роутере"""

from typing import Any, Dict, List, Optional, Type
from datetime import datetime
from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.utils.alchemy_utils import create_search_conditions
from app.core.utils.alchemy_utils import ModelType
from app.core.services.logger import logger
# from app.core.utils.common_utils import get_text_model_fields


class Repository:
    # model: ModelType

    @classmethod
    async def create(cls, obj: ModelType, model: ModelType, session: AsyncSession) -> ModelType:
        session.add(obj)
        await session.commit()  # в сложных запросах когда нужно получить id и добавиить его в связанную таблицу
        await session.refresh(obj)
        return obj

    @classmethod
    async def patch(cls, obj: ModelType, data: Dict[str, Any],
                    session: AsyncSession) -> Optional[ModelType]:
        # obj = await cls.get_by_id(id, model, session)
        for k, v in data.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        await session.commit()
        await session.refresh()
        return obj

    @classmethod
    async def delete(cls, obj: ModelType, session: AsyncSession) -> bool:
        try:
            await session.delete(obj)
            await session.commit()
            return True
        except Exception as e:
            logger.error(f'ошибка удаления записи: {e}')
            return False

    @classmethod
    def get_query(cls, model: ModelType):
        """
        Переопределяемый метод.
        Возвращает select() с нужными selectinload.
        По умолчанию — без связей.
        """
        return select(model)

    @classmethod
    async def get_by_id(cls, id: int, model: ModelType, session: AsyncSession) -> Optional[ModelType]:
        """
        get one record by id
        """
        try:
            stmt = cls.get_query(model).where(model.id == id)
            result = await session.execute(stmt)
            obj = result.scalar_one_or_none()
            return obj
        except Exception:
            return None

    @classmethod
    async def get_by_obj(cls, data: dict, model: Type[ModelType], session: AsyncSession) -> Optional[ModelType]:
        valid_fields = {key: value for key, value in data.items()
                        if hasattr(model, key)}
        if not valid_fields:
            return None
        stmt = select(model).filter_by(**valid_fields)
        result = await session.execute(stmt)
        item = result.scalar_one_or_none()
        return item

    @classmethod
    async def get_all(cls, after_date: datetime, skip: int,
                      limit: int, model: ModelType, session: AsyncSession, ) -> tuple:
        # Запрос с загрузкой связей и пагинацией
        stmt = cls.get_query(model).where(model.updated_at > after_date).offset(skip).limit(limit)
        total = await cls.get_count(after_date, model, session)
        result = await session.execute(stmt)
        items = result.scalars().all()
        return items, total

    @classmethod
    async def get(cls, after_date: datetime, model: ModelType, session: AsyncSession, ) -> list:
        # Запрос с загрузкой связей NO PAGINATION
        stmt = cls.get_query(model).where(model.updated_at > after_date)
        result = await session.execute(stmt)
        items = result.scalars().all()
        return items

    @classmethod
    async def get_by_field(cls, field_name: str, field_value: Any, model: ModelType, session: AsyncSession):
        """
            не гибкий поиск по одному полю. оставлен для совместимости. лучше использовать
            get_by_fields
        """
        try:
            stmt = select(model).where(getattr(model, field_name) == field_value)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            raise Exception(f'repo.get_by_field: {field_name=} {field_value=}, {model.__name__=}, {e}')

    @classmethod
    async def get_by_fields(cls, filter: dict, model: ModelType, session: AsyncSession):
        """
            фильтр по нескольким полям
            filter = {<имя поля>: <искомое значение>, ...},
            AND
        """
        try:
            conditions = []
            for key, value in filter.items():
                column = getattr(model, key)
                if value is None:
                    conditions.append(column.is_(None))
                else:
                    conditions.append(column == value)
            stmt = select(model).where(and_(*conditions)).limit(1)
            # stmt = select(model).filter_by(**filter)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            raise Exception(f'repo.get_by_fields: {filter=}, {model.__name__=}, {e}')

    @classmethod
    async def get_count(cls, after_date: datetime, model: ModelType, session: AsyncSession) -> int:
        count_stmt = select(func.count()).select_from(model).where(model.updated_at > after_date)
        count_result = await session.execute(count_stmt)
        total = count_result.scalar()
        return total

    @classmethod
    async def search_in_main_table(cls,
                                   search_str: str,
                                   model: Type[ModelType],
                                   session: AsyncSession,
                                   skip: int = None,
                                   limit: int = None,
                                   and_condition: dict = None) -> Optional[List[ModelType]]:
        """
        Поиск по всем заданным текстовым полям основной таблицы
        если указана pagination - возвращвет pagination
        :param search_str:  текстовое условие поиска
        :type search_str:   str
        :param model:       модель
        :type model:        sqlalchemy model
        :param session:     async session
        :type session:      async session
        :param skip:        сдвиг на кол-во записей (для пагинации)
        :type skip:         int
        :param limit:       кол-во записей
        :type limit:        int
        :param and_condition:   дополнительные условия _AND
        :type and_condition:    dict
        :return:                Optional[List[ModelType]]
        :rtype:                 Optional[List[ModelType]]
        """
        try:
            conditions = create_search_conditions(model, search_str, 1)
            # query = cls.get_query(model).where(or_(*conditions))
            query = cls.get_query(model).where(conditions)
            # получаем общее количество записей удовлетворяющих условию
            # count = select(func.count()).select_from(model).where(or_(*conditions))
            count = select(func.count()).select_from(model).where(conditions)
            result = await session.execute(count)
            total = result.scalar()
            # Добавляем пагинацию если указано
            if limit is not None:
                query = query.limit(limit)
            if skip is not None:
                query = query.offset(skip)
            result = await session.execute(query)
            records = result.scalars().all()
            return (records if records else [], total)
        except Exception as e:
            logger.error(f'ошибка search_in_main_table: {e}')
            print(f'search_in_main_table.error: {e}')

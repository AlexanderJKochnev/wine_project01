# app/core/repositories/sqlalchemy_repository.py
""" не использовать Depends в этом контексте, он не входит в FastApi - только в роутере"""
from abc import ABCMeta
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Type, Union
# from sqlalchemy.dialects import postgresql
from sqlalchemy import and_, func, select, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
# from sqlalchemy.sql.elements import ColumnElement
from app.core.services.logger import logger
from app.core.utils.alchemy_utils import (create_enum_conditions, create_search_conditions,
                                          create_search_conditions2, ModelType)
from app.core.utils.alchemy_utils import get_sqlalchemy_fields


class RepositoryMeta(ABCMeta):
    _registry = {}

    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)
        # Регистрируем сам класс, а не его экземпляр
        if not attrs.get('__abstract__', False):
            key = name.lower().replace('repository', '')
            cls._registry[key] = new_class  # ← Сохраняем класс!
        return new_class


class Repository(metaclass=RepositoryMeta):
    __abstract__ = True
    model: ModelType

    @classmethod
    async def create(cls, obj: ModelType, model: ModelType, session: AsyncSession) -> ModelType:
        """ создание записи """
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    @classmethod
    async def patch(cls, obj: ModelType,
                    data: Dict[str, Any], session: AsyncSession) -> Optional[ModelType]:
        """
        редактирование записи
        :param obj: редактируемая запись
        :param data: изменения в редактируемую запись
        """
        try:
            for k, v in data.items():
                if hasattr(obj, k):
                    setattr(obj, k, v)
            await session.commit()
            await session.refresh(obj)
            return obj
        except IntegrityError as e:
            await session.rollback()
            error_str = str(e.orig).lower()
            if 'unique constraint' in error_str or 'duplicate key' in error_str:
                return "unique_constraint_violation"
            elif 'foreign key constraint' in error_str:
                return "foreign_key_violation"
            return f"integrity_error: {error_str}"
        except Exception as e:
            await session.rollback()
            return f"database_error: {str(e)}"

    @classmethod
    async def delete(cls, obj: ModelType, session: AsyncSession) -> bool:
        """
        удаление записи
        :param obj: instance
        """
        try:
            await session.delete(obj)
            await session.commit()
            return True
        except IntegrityError as e:
            await session.rollback()
            # Проверяем, является ли ошибка Foreign Key violation
            error_str = str(e.orig)
            if "foreign key constraint" in error_str.lower() or "violates foreign key constraint" in error_str.lower():
                return "foreign_key_violation"
            return f"integrity_error: {error_str}"
        except Exception as e:
            await session.rollback()
            return f"database_error: {str(e)}"

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
        stmt = cls.get_query(model).where(model.id == id)
        result = await session.execute(stmt)
        obj = result.scalar_one_or_none()
        return obj

    @classmethod
    async def get_by_obj(cls, data: dict, model: Type[ModelType], session: AsyncSession) -> Optional[ModelType]:
        """
        получение instance ло совпадению данных данным
        :param data:
        :type data:
        :param model:
        :type model:
        :param session:
        :type session:
        :return:
        :rtype:
        """
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
                                   limit: int = None) -> Optional[List[ModelType]]:
        """
        НЕ ИСПОЛЬЗУЕТСЯ ПОСЛЕ ПРОВЕРКИ УДАЛИТЬ
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

    @classmethod
    async def search_by_enum(cls, enum: str,
                             model: Type[ModelType],
                             session: AsyncSession,
                             field_name: str = None) -> Optional[ModelType]:
        """
        поиск по ключевому полю. на входе enum. на выходе 1 запись
        """
        conditions = create_enum_conditions(model, enum, field_name)
        stmt = select(model).where(conditions).limit(1)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    def apply_search_filter(cls, model: Union[Select[Tuple], ModelType], **kwargs):
        """
            переопределяемый метод.
            в kwargs - условия поиска
            применяет фильтры и возвращает
            1. если на входе model - выборку с selectinload
            2. на входе Select - просто select (count, ...)
        """
        if not isinstance(model, Select):   # подсчет количества
            query = cls.get_query(model)
        else:
            query = model
        search_str: str = kwargs.get('search_str')
        if search_str:
            search_cond = create_search_conditions2(cls.model, search_str)
            query = query.where(search_cond)
        return query

    @classmethod
    async def search(cls,
                     model: Type[ModelType],
                     session: AsyncSession,
                     **kwargs) -> Optional[List[ModelType]]:
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
            query = cls.apply_search_filter(cls.get_query(model), **kwargs)
            total = 0
            # Добавляем пагинацию если указано и общее кол-во записей
            limit, skip = kwargs.get('limit'), kwargs.get('skip')
            if limit is not None:
                # общее кол-во записей удовлетворяющих условию
                count_stmt = cls.apply_search_filter(select(func.count()).select_from(cls.get_query(model)),
                                                     **kwargs)
                result = await session.execute(count_stmt)
                total = result.scalar()
                query = query.limit(limit)
            if skip is not None:
                query = query.offset(skip)
            result = await session.execute(query)
            records = result.scalars().all()
            return (records if records else [], total)
        except Exception as e:
            logger.error(f'ошибка search: {e}')

    @classmethod
    async def get_list_view_page(cls, skip: int, limit: int,
                                 model: ModelType, session: AsyncSession, ) -> Tuple[List[tuple], int]:
        # Запрос с загрузкой связей и пагинацией
        stmt = cls.get_query(model).offset(skip).limit(limit)
        fields = get_sqlalchemy_fields(stmt, exclude_list=['description*',])
        stmt = select(*fields)
        total = await cls.get_count(model, session)
        result = await session.execute(stmt)
        rows = result.all()
        print(f'======{model.__name__=}')
        for row in rows:
            print('==', type(row), row)
        return rows, total

    @classmethod
    async def get_list_view(cls, model: ModelType, session: AsyncSession, ) -> List[Tuple]:
        # Запрос с загрузкой связей без пагинации (для справочников)
        stmt = cls.get_query(model)
        # compiled_pg = stmt.compile(dialect=postgresql.dialect())
        result = await session.execute(stmt)
        rows = result.scalar().all()
        result = [row._mapping for row in rows]
        return result

    @classmethod
    async def get_nodate(cls, model: ModelType, session: AsyncSession, ) -> list:
        # Запрос с загрузкой связей NO PAGINATION
        stmt = cls.get_query(model)
        result = await session.execute(stmt)
        items = result.scalars().all()
        return items

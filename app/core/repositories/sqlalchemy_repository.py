# app/core/repositories/sqlalchemy_repository.py
""" не использовать Depends в этом контексте, он не входит в FastApi - только в роутере"""

from typing import Any, Dict, List, Optional, Type, TypeVar

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta

from app.core.services.logger import logger
from app.core.utils.common_utils import get_text_model_fields

ModelType = TypeVar("ModelType", bound=DeclarativeMeta)


class Repository:
    # model: ModelType

    @classmethod
    async def create(cls, obj: ModelType, model: ModelType, session: AsyncSession) -> ModelType:
        session.add(obj)
        await session.flush()  # в сложных запросах когда нужно получить id и добавиить его в связанную таблицу
        # commit делаем в сервисе - для групповых операций
        return obj

    @classmethod
    async def patch(cls, obj: ModelType, data: Dict[str, Any],
                    session: AsyncSession) -> Optional[ModelType]:
        # obj = await cls.get_by_id(id, model, session)
        for k, v in data.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        await session.flush()
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
                        if hasattr(model, key) and not key.endswith('_id')}
        if not valid_fields:
            return None

        stmt = select(model).filter_by(**valid_fields)
        result = await session.execute(stmt)
        item = result.scalar_one_or_none()
        return item

    @classmethod
    async def get_all(cls, skip, limit, model: ModelType, session: AsyncSession, ) -> tuple:
        # Запрос с загрузкой связей и пагинацией
        stmt = cls.get_query(model).offset(skip).limit(limit)
        total = await cls.get_count(model, session)
        result = await session.execute(stmt)
        items = result.scalars().all()
        return items, total

    @classmethod
    async def get(cls, model: ModelType, session: AsyncSession, ) -> list:
        # Запрос с загрузкой связей NO PAGINATION
        stmt = cls.get_query(model)
        result = await session.execute(stmt)
        items = result.scalars().all()
        return items

    @classmethod
    async def get_by_field(cls, field_name: str, field_value: Any, model: ModelType, session: AsyncSession):
        stmt = select(model).where(getattr(model, field_name) == field_value)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_count(cls, model: ModelType, session: AsyncSession) -> int:
        count_stmt = select(func.count()).select_from(model)
        count_result = await session.execute(count_stmt)
        total = count_result.scalar()
        return total

    @classmethod
    async def search_in_main_table(cls,
                                   search_query: str,
                                   page: int,
                                   page_size: int,
                                   skip: int,
                                   model: ModelType,
                                   session: AsyncSession) -> List[Any]:
        """Поиск по всем заданным текстовым полям основной таблицы"""
        items = []
        total = 0
        try:
            query = cls.get_query(model)     # все записи
            text_fields = get_text_model_fields(model)
            conditions = []
            for field in text_fields:
                conditions.append(getattr(model, field).ilike(f"%{search_query}%"))
            if conditions:
                query = query.filter(or_(*conditions))
            # total_query = select(func.count()).select_from(query)
            total_tmp = await session.execute(select(func.count()).select_from(query))
            total = total_tmp.scalar()

            query = query.offset(skip).limit(page_size)
            result = await session.execute(query)
            items = result.scalars().all()
            has_next = skip + len(items) < total
        except Exception as e:
            logger.error(f'ошибка search_in_main_table: {e}')
        finally:
            result = {"items": items,
                      "total": total,
                      "page": page,
                      "page_size": page_size,
                      "has_next": has_next,
                      "has_prev": page > 1}
            return result


"""
    @classmethod
    async def search_with_relations(
            cls, search_query: Optional[str], main_text_fields: Optional[List[str]] = None,
            relation_fields: Optional[Dict[str, List[str]]] = None, page: int = 1, page_size: int = 20
            ) -> Tuple[List[Item], int]:
        # Поиск по текстовым полям основной таблицы и связанных таблиц с пагинацией
        if not search_query:
            stmt = select(Item)
            count_stmt = select(func.count()).select_from(Item)
        else:
            main_text_fields = main_text_fields or ['name', 'description']
            relation_fields = relation_fields or {}

            conditions = []

            # Поля основной таблицы
            for field in main_text_fields:
                if hasattr(Item, field):
                    conditions.append(getattr(Item, field).ilike(f"%{search_query}%"))

            # Поля связанных таблиц
            for relation_name, fields in relation_fields.items():
                if hasattr(Item, relation_name):
                    relation_attr = getattr(Item, relation_name)
                    rel_model = relation_attr.property.mapper.class_

                    for field in fields:
                        if hasattr(rel_model, field):
                            # Создаем подзапрос для связанной таблицы
                            subquery = select(Item.id).join(
                                    rel_model, getattr(Item, f"{relation_name}_id") == rel_model.id
                                    ).where(
                                    getattr(rel_model, field).ilike(f"%{search_query}%")
                                    )
                            conditions.append(Item.id.in_(subquery))

            if not conditions:
                return [], 0

            stmt = select(Item).where(or_(*conditions))
            count_stmt = select(func.count()).select_from(Item).where(or_(*conditions))

        # Загружаем связанные данные
        stmt = stmt.options(
                selectinload(Item.category), selectinload(Item.tags)
                )

        # Пагинация
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        result = await cls.session.execute(stmt)
        items = result.scalars().all()

        count_result = await cls.session.execute(count_stmt)
        total_count = count_result.scalar()

        return items, total_count
"""

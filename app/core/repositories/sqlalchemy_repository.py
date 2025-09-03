# app/core/repositories/sqlalchemy_repository.py
""" не использовать Depends в этом контексте, он не входит в FastApi - только в роутере"""

from typing import Any, Dict, Generic, List, Optional, TypeVar

from sqlalchemy import func, select, or_, and_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta
from app.core.utils.common_utils import get_text_model_fields
from app.core.services.logger import logger

ModelType = TypeVar("ModelType", bound=DeclarativeMeta)


class Repository(Generic[ModelType]):
    model: ModelType

    def get_query(self):
        """
        Переопределяемый метод.
        Возвращает select() с нужными selectinload.
        По умолчанию — без связей.
        """
        return select(self.model)

    async def create(self, data: Dict[str, Any], session: AsyncSession) -> ModelType:
        """ create & return record """
        # stmt = insert(self.model).values(**data).returning(self.model)
        # result = await session.execute(stmt)
        # obj = result.scalar_one()

        obj = self.model(**data)
        session.add(obj)
        await session.flush()  # в сложных запросах когда нужно получить id и добавиить его в связанную таблицу
        await session.commit()
        await session.refresh(obj)
        return obj

    async def get_by_id(self, id: int, session: AsyncSession) -> Optional[ModelType]:
        """
        get one record by id
        """
        stmt = self.get_query().where(self.model.id == id)
        result = await session.execute(stmt)
        obj = result.scalar_one_or_none()
        return obj

    async def get_all(self, skip, limit, session: AsyncSession, ) -> dict:
        # Запрос с загрузкой связей и пагинацией
        stmt = self.get_query().offset(skip).limit(limit)
        result = await session.execute(stmt)
        items = result.scalars().all()
        return items

    async def patch(self, id: Any, data: Dict[str, Any], session: AsyncSession) -> Optional[ModelType]:
        obj = await self.get_by_id(id, session)
        if not obj:
            return None
        for k, v in data.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def delete(self, id: Any, session: AsyncSession) -> bool:
        try:
            obj = await self.get_by_id(id, session)
            if not obj:
                return False
            await session.delete(obj)
            await session.commit()
            return True
        except Exception as e:
            logger.error(f'ошибка удаления записи: {e}')
            return False

    async def get_by_field(self, field_name: str, field_value: Any, session: AsyncSession):
        stmt = select(self.model).where(getattr(self.model, field_name) == field_value)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_count(self, session: AsyncSession) -> int:
        count_stmt = select(func.count()).select_from(self.model)
        count_result = await session.execute(count_stmt)
        total = count_result.scalar()
        return total

    async def search_in_main_table(self,
                                   search_query: str,
                                   page: int,
                                   page_size: int,
                                   skip: int,
                                   session: AsyncSession) -> List[Any]:
        """Поиск по всем заданным текстовым полям основной таблицы"""
        items = []
        total = 0
        try:
            query = self.get_query()     # все записи
            text_fields = get_text_model_fields(self.model)
            conditions = []
            for field in text_fields:
                conditions.append(getattr(self.model, field).ilike(f"%{search_query}%"))
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

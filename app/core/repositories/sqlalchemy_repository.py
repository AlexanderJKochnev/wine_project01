# app/core/repositories/sqlalchemy_repository.py
""" не использовать Depends в этом контексте, он не входит в FastApi - только в роутере"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Dict, Optional, TypeVar, Generic
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy import select, func
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

    async def update(self, id: Any, data: Dict[str, Any], session: AsyncSession) -> Optional[ModelType]:
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

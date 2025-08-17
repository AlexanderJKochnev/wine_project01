# app/core/repositories/sqlalchemy_repository.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Dict, Optional, TypeVar, Generic
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy import select, func
from app.core.config.database.db_async import get_db

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

    async def create(self, data: Dict[str, Any], session: AsyncSession = Depends(get_db)) -> ModelType:
        """ create & return record """
        obj = self.model(**data)
        session.add(obj)
        # await session.flush()  # в сложных запросах когда нужно получить id и добавиить его в связанную таблицу
        await session.commit()
        await session.refresh(obj)
        return obj

    async def get_by_id(self, id: int, session: AsyncSession = Depends(get_db)) -> Optional[ModelType]:
        """
        get one record by id
        """
        stmt = self.get_query().where(self.model.id == id)
        result = await session.execute(stmt)
        obj = result.scalar_one_or_none()
        return obj

    async def get_all(self, skip, limit, session: AsyncSession = Depends(get_db)) -> dict:
        # Запрос с загрузкой связей и пагинацией
        stmt = self.get_query().offset(skip).limit(limit)
        result = await session.execute(stmt)
        items = result.scalars().all()
        return items

    async def update(self, id: int, data: Dict[str, Any],
                     session: AsyncSession = Depends(get_db)) -> Optional[ModelType]:
        obj = await self.get_by_id(id, session)
        if not obj:
            return None
        for k, v in data.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def delete(self, id: int, session: AsyncSession = Depends(get_db)) -> bool:
        obj = await self.get_by_id(id, session)
        print(f'{obj=}')
        if not obj:
            return False
        await session.delete(obj)
        await session.commit()
        return True

    async def get_by_field(self, field_name: str, field_value: Any, session: AsyncSession = Depends(get_db)):
        stmt = select(self.model).where(getattr(self.model, field_name) == field_value)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_count(self, session: AsyncSession = Depends(get_db)) -> Optional[int]:
        count_stmt = select(func.count()).select_from(self.model)
        count_result = await session.execute(count_stmt)
        total = count_result.scalar()
        return total

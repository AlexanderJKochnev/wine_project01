# app/core/repositories/sqlalchemy_repo2.py
"""
    функция для генерации репозиториев на базе model
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Any, Dict, Optional, Type, TypeVar, Generic
from sqlalchemy.orm import DeclarativeMeta

ModelType = TypeVar("ModelType", bound=DeclarativeMeta)


class Repository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model
        self.pk_name = self._get_pk_name()

    def _get_pk_name(self) -> str:
        mapper = self.model.__mapper__
        pk_cols = list(mapper.primary_key)
        if len(pk_cols) != 1:
            raise NotImplementedError("Composite PK не поддерживается в фабрике")
        return pk_cols[0].name

    async def create(self, db: AsyncSession, data: Dict[str, Any]) -> ModelType:
        obj = self.model(**data)
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def get_by_id(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        stmt = select(self.model).where(getattr(self.model, self.pk_name) == id)
        result = await db.scalars(stmt)
        return result.first()

    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        result = await db.scalars(stmt)
        return result.all()

    async def update(self, db: AsyncSession, id: Any, data: Dict[str, Any]) -> Optional[ModelType]:
        obj = await self.get_by_id(db, id)
        if not obj:
            return None
        for k, v in data.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def delete(self, db: AsyncSession, id: Any) -> bool:
        obj = await self.get_by_id(db, id)
        if not obj:
            return False
        await db.delete(obj)
        await db.commit()
        return True

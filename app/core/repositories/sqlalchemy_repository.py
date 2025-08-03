# app/core/repositories/sqlalchemy_repository.py

from typing import Type, TypeVar, Optional, Generic, List
from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.models.base_model import Base
from base_repository import AbstractRepository
from app.core.config.database import db_helper

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class SqlAlchemyRepository1(AbstractRepository,
                            Generic[ModelType, CreateSchemaType,
                                    UpdateSchemaType]):

    def __init__(self, model: Type[ModelType], db_session: AsyncSession):
        self._session_factory = db_session
        self.model = model

    async def create(self, data: CreateSchemaType) -> ModelType:
        async with self._session_factory() as session:
            instance = self.model(**data)
            session.add(instance)
            await session.commit()
            await session.refresh(instance)
            return instance

    async def update(self, data: UpdateSchemaType, **filters) -> ModelType:
        async with self._session_factory() as session:
            stmt = update(
                self.model).values(**data).filter_by(
                **filters).returning(self.model)
            res = await session.execute(stmt)
            await session.commit()
            return res.scalar_one()

    async def delete(self, **filters) -> None:
        async with self._session_factory() as session:
            await session.execute(delete(self.model).filter_by(**filters))
            await session.commit()

    async def get_single(self, **filters) -> Optional[ModelType] | None:
        async with self._session_factory() as session:
            row = await session.execute(
                select(self.model).filter_by(**filters))
            return row.scalar_one_or_none()

    async def get_multi(
            self,
            order: str = "id",
            limit: int = 100,
            offset: int = 0
    ) -> list[ModelType]:
        async with self._session_factory() as session:
            stmt = select(
                self.model).order_by(*order).limit(limit).offset(offset)
            row = await session.execute(stmt)
            return row.scalars().all()


class SqlAlchemyRepository:
    model = None
    _session_factory = db_helper.get_db_session

    @classmethod
    async def add(cls, data: CreateSchemaType) -> ModelType | None:
        """ add single instance """
        async with cls._session_factory() as session:
            try:
                instance = cls.model(**data.dict())
                session.add(instance)
                await session.flush()
                await session.commit()
                result = instance
            except Exception:
                session.rollback()
                result = None
        return result

    @classmethod
    async def add_all(
            cls,
            dataset: List[CreateSchemaType]
    ) -> List[ModelType]:
        """ add all instances from the list """
        result: list = []
        async with cls._session_factory() as session:
            try:
                instances = [cls.model(**data.dict())
                             for data in dataset]
                session.add_all(instances)
                await session.flush()
                await session.commit()
                result = instances
            except Exception:
                session.rollback()
                result = None
            finally:
                return result

    @classmethod
    async def delete(cls, instance: ModelType) -> bool:
        """ Delete single instance """
        async with cls._session_factory() as session:
            await session.delete(instance)
            result = instance in session.deleted
            await session.commit()
            return result

    @classmethod
    async def delete_all(cls, instances: List[ModelType]) -> bool:
        """ Delete single instance by id """
        async with (cls._session_factory() as session):
            for instance in instances:
                await session.delete(instance)
            result = all((instance in session.deleted
                          for instance in instances))
            await session.commit()
            return result

    @classmethod
    async def get(cls, id) -> Optional[ModelType] | None:
        """ get single record by id """
        async with cls._session_factory() as session:
            instance = await session.get(cls.model, id)
            return instance

    @classmethod
    async def get_all(
            cls,
            order: str = "id",
            limit: int = 100,
            offset: int = 0
    ) -> list[ModelType]:
        async with cls._session_factory() as session:
            stmt = select(
                cls.model).order_by(*order).limit(limit).offset(offset)
            stmt = select(cls.model)
            row = await session.execute(stmt)
            return row.scalars().all()

    @classmethod
    async def find(cls, **filters) -> List[ModelType] | None:
        """ find one or more instance"""
        async with cls._session_factory() as session:
            rows = await session.execute(
                select(cls.model).filter_by(**filters))
            return rows.scalars().all()

    @classmethod
    async def update(cls, data: UpdateSchemaType, **filters) -> ModelType:
        """ update single record by id """
        async with cls._session_factory() as session:
            stmt = update(
                cls.model).values(**data.dict()).filter_by(
                **filters).returning(cls.model)
            res = await session.execute(stmt)
            await session.commit()
            return res.scalar_one()

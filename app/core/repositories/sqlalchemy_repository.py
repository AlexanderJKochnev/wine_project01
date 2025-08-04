# app/core/repositories/sqlalchemy_repository.py

from typing import TypeVar, Optional, List
from pydantic import BaseModel
from sqlalchemy import select, update
from app.core.models.base_model import Base
from app.core.config.database.db_helper import db_help

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class SqlAlchemyRepository:
    model = None
    _session_factory = db_help.get_db_session

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

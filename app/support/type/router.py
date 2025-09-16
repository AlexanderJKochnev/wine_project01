# app/support/type/auth.py

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.type.model import Type
from app.support.type.repository import TypeRepository
from app.support.type.schemas import (TypeRead, TypeCreate, TypeUpdate,
                                      TypeCreateRelation, TypeCreateResponseSchema)
from app.support.type.service import TypeService


class TypeRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Type,
            repo=TypeRepository,
            create_schema=TypeCreate,
            read_schema=TypeRead,
            create_schema_relation=TypeCreateRelation,
            create_response_schema=TypeCreateResponseSchema,
            prefix="/types",
            tags=["types"],
            service=TypeService
        )

    async def create(self, data: TypeCreate, session: AsyncSession = Depends(get_db)) -> TypeCreateResponseSchema:
        return await super().create(data, session)

    async def patch(self, id: int,
                    data: TypeUpdate, session: AsyncSession = Depends(get_db)) -> TypeCreateResponseSchema:
        return await super().patch(id, data, session)

    async def create_relation(self, data: TypeCreateRelation,
                              session: AsyncSession = Depends(get_db)) -> TypeRead:
        result = await super().create_relation(data, session)
        return result

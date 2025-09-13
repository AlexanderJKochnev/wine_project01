# app/support/item/auth.py

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.item.model import Item
from app.support.item.repository import ItemRepository
from app.support.item.schemas import (ItemRead, ItemCreate, ItemUpdate, ItemCreateRelationSchema,
                                      ItemCreateResponseSchema)
from app.support.item.service import ItemService


class ItemRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Item,
            repo=ItemRepository,
            create_schema=ItemCreate,
            read_schema=ItemRead,
            prefix="/items",
            tags=["items"],
            create_response_schema=ItemCreateResponseSchema,
            create_schema_relation=ItemCreateRelationSchema,
            service=ItemService
        )

    async def create(self, data: ItemCreate,
                     session: AsyncSession = Depends(get_db)) -> ItemCreateResponseSchema:
        return await super().create(data, session)

    async def patch(self, id: int, data: ItemUpdate,
                    session: AsyncSession = Depends(get_db)) -> ItemCreateResponseSchema:
        return await super().patch(id, data, session)

# app/preact/drink/router.py
from typing import Any, Dict, Type
from app.core.models.base_model import DeclarativeBase
from fastapi import Body, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.utils.pydantic_utils import sqlalchemy_to_pydantic_post, get_pyschema
from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.item.model import Item
from app.support.item.repository import ItemRepository
from app.mongodb.service import ThumbnailImageService


class MainRouter(BaseRouter):
    def __init__(self, prefix: str = '/main', **kwargs):
        super().__init__(
            model=Item, prefix=prefix, repo=ItemRepository
        )
        self.image_service: ThumbnailImageService = Depends()
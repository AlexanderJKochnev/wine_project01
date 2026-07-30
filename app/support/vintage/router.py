# app.support.vintage.router.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.vintage.model import Classification, Designation, VintageConfig
from app.support.vintage.repository import (ClassificationRepository, DesignationRepository,  # noqa: F401
                                            VintageConfigRepository)  # noqa: F401
from app.support.vintage.schemas import (ClassificationCreate, DesignationCreate, VintageConfigCreate)
from app.support.vintage.service import ClassificationService, DesignationService, VintageConfigService  # noqa: F401


class VintageConfigRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=VintageConfig,
            prefix="/vintage_config",
        )

    async def create(self, data: VintageConfigCreate,
                     session: AsyncSession = Depends(get_db)):
        return await super().create(data, session)


class DesignationRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Designation,
            prefix="/designation",
        )

    async def create(self, data: DesignationCreate,
                     session: AsyncSession = Depends(get_db)):
        return await super().create(data, session)


class ClassificationRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Classification,
            prefix="/classification",
        )

    async def create(self, data: ClassificationCreate,
                     session: AsyncSession = Depends(get_db)):
        return await super().create(data, session)

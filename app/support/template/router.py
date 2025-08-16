# app/support/template/router.py
"""
    1. Выполни замену Template/template на актуальное имя следующим образом
    1.1. замени templates на выбранное имя (мн.число по правилам англ языка в нижнем регистре)
        например для Country это будет ccountries
    1.2. Template -> Country
    1.3. template -> country
    2. Удали эту инструкцию
"""

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.template.model import Template
from app.support.template.repository import TemplateRepository
from app.support.template.schemas import TemplateRead, TemplateCreate, TemplateUpdate


class TemplateRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Template,
            repo=TemplateRepository,
            create_schema=TemplateCreate,
            update_schema=TemplateUpdate,
            read_schema=TemplateRead,
            prefix="/templates",
            tags=["templates"]
        )
        self.setup_routes()

    async def create(self, data: TemplateCreate, session: AsyncSession = Depends(get_db)) -> TemplateRead:
        return await super().create(data, session)

    async def update(self, id: int, data: TemplateUpdate,
                     session: AsyncSession = Depends(get_db)) -> TemplateRead:
        return await super().update(id, data, session)


router = TemplateRouter().router

# app/support/template/router.py
"""
замени Template на имя модели в единственном числе с сохранением регистра
проверь словари lbl и paging
"""

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.config.database.db_noclass import get_db
from app.core.routers.base import BaseRouter
from app.support.template.models import Template
from app.support.template.repository import TemplateRepository
from app.support.template.schemas import TemplateRead, TemplateCreate, TemplateUpdate

# список подсказок, в дальнейшем загрузить в бд на разных языках и выводить на языке интерфейса
lbl: dict = {'get': 'Список напитков',
             'prefix': 'Напитки',
             'item': 'Напиток',
             'items': 'Напитки',
             'notfound': 'не найден(а)'}


class TemplateRouter(BaseRouter[TemplateCreate, TemplateUpdate, TemplateRead]):
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

# app/support/template/auth.py
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
from app.support.region.model import Template
from app.support.region.repository import TemplateRepository
from app.support.region.schemas import TemplateRead, TemplateCreate, TemplateUpdate, TemplateCreateResponseSchema


class TemplateRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Template,
            repo=TemplateRepository,
            create_schema=TemplateCreate,
            patch_schema=TemplateUpdate,
            read_schema=TemplateRead,
            prefix="/regions",
            tags=["regions"]
        )
        self.create_response_schema = TemplateCreateResponseSchema

    def setup_routes(self):
        """Настраивает маршруты"""
        self.router.add_api_route("", self.create, methods=["POST"], response_model=self.create_response_schema)
        self.router.add_api_route("", self.get, methods=["GET"], response_model=self.paginated_response)
        self.router.add_api_route("/{id}", self.get_one, methods=["GET"], response_model=self.read_schema)
        self.router.add_api_route("/{id}", self.patch, methods=["PATCH"], response_model=self.read_schema)
        self.router.add_api_route("/{id}", self.delete, methods=["DELETE"], response_model=self.delete_response)

    async def create(self, data: TemplateCreate, session: AsyncSession = Depends(get_db)) -> TemplateRead:
        return await super().create(data, session)

    async def patch(self, id: int, data: TemplateUpdate,
                    session: AsyncSession = Depends(get_db)) -> TemplateRead:
        return await super().patch(id, data, session)

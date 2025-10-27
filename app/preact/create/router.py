# app/preact/create/router.py

from typing import Any, Dict

from fastapi import APIRouter, Body, Depends, Request
# from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_active_user_or_internal
from app.core.config.database.db_async import get_db
from app.core.repositories.sqlalchemy_repository import Repository
from app.core.routers.base import HTTPException, logger
from app.core.services.service import Service
from app.core.utils.pydantic_utils import sqlalchemy_to_pydantic_post
from app.support import (Category, Country, Food, Region, Subcategory, Subregion, Superfood, Varietal)


class CreateRouter:
    def __init__(self):
        prefix = 'create'
        self.tags, self.prefix = [f'{prefix}'], f'/{prefix}'
        self.service = Service
        self.repo = Repository
        self.source = {'categories': Category,
                       'subcategories': Subcategory,
                       'countries': Country,
                       'regions': Region,
                       'subregions': Subregion,
                       'superfoods': Superfood,
                       'foods': Food,
                       'varietals': Varietal}
        self.schemas_generator(self.source)
        self.router = APIRouter(prefix=self.prefix, tags=self.tags,
                                dependencies=[Depends(get_active_user_or_internal)])
        self.setup_routes()

    def __set_schema__(self, model):
        setattr(self, f'{model.__name__}Create', sqlalchemy_to_pydantic_post(model))

    def __get_schemas__(self, model):
        return getattr(self, f'{model.__name__}Create')

    def schemas_generator(self, source: dict):
        for model in self.source.values():
            self.__set_schema__(model)

    def routes_generator(self, source: dict):
        """
            возвращает список
            [prefix, response_model]
        """
        return ((f'/{key}', self.__get_schemas__(val)) for key, val in source.items())

    def setup_routes(self):
        for prefix, response_model in self.routes_generator(self.source):
            self.router.add_api_route(prefix,
                                      self.create,
                                      methods=["POST"],
                                      response_model=response_model)

    def __path_decoder__(self, path: str, tier: int = 2):
        """ декодирует url.path справа"""
        result = path.rsplit('/')
        mod = result[-1]
        return mod

    async def create(self, request: Request, data: Dict[str, Any] = Body(...),
                     session: AsyncSession = Depends(get_db)):
        try:
            current_path = request.url.path
            tmp = self.__path_decoder__(current_path)
            model = self.source.get(tmp)
            schema = self.__get_schemas__(model)
            model_data = schema(**data)
            obj = await self.service.get_or_create(model_data, self.repo, model, session)
            return obj
        except Exception as e:
            await session.rollback()
            logger.error(f"Unexpected error in create_item: {e}")
            raise HTTPException(
                status_code=505,
                detail=f'Create Fault, {e}'
            )

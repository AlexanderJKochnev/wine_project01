# app/preact/create/router.py

from typing import Dict

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_active_user_or_internal
from app.core.config.database.db_async import get_db
from app.core.config.project_config import settings
from app.core.services.service import Service
from app.support import (Category, Country, Food, Region, Subcategory, Subregion, Superfood, Varietal)
from app.core.utils.pydantic_utils import sqlalchemy_to_pydantic_post

class CreateRouter:
    def __init__(self):
        prefix = 'create'
        self.tags, self.prefix = [f'{prefix}'], f'/{prefix}'
        self.service = Service
        self.source = {'categories': Category,
                       'subcategories': Subcategory,
                       'countries': Country,
                       'regions': Region,
                       'subregions': Subregion,
                       # 'customers': (Customer,),
                       'superfoods': Superfood,
                       'foods': Food,
                       'varietal': Varietal}
        self.schemas_generator(self.source)
        self.router = APIRouter(prefix=self.prefix, tags=self.tags,
                                dependencies=[Depends(get_active_user_or_internal)])

    def set_schema(self, model):
        setattr(self, f'{model.__name__}Create', sqlalchemy_to_pydantic_post(model))

    def get_schemas(self, model):
        return getattr(self, f'{model.__name__}Create')

    def schemas_generator(self, source: dict):
        for val in self.source.values():
            self.set_schema(val)

    def
# app/support/handbook/router.py
"""
    роутер для ListView для всех кроме Drink & Items
    выводит только словари  id: name
    по языкам
"""
from typing import Dict

from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.utils.alchemy_utils import get_lang_prefix
from app.auth.dependencies import get_active_user_or_internal
from app.core.config.database.db_async import get_db
from app.core.config.project_config import settings
from app.core.services.service import Service
from app.support import (Category, Country, Food, Region, Subcategory, Subregion, Superfood, Varietal)
# from app.support import (CategoryRead, CountryRead, FoodRead, RegionRead, SubcategoryRead,
#                         SuperfoodRead, VarietalRead, SubregionRead)


class GetRouter:
    def __init__(self):
        prefix = 'get'
        self.tags, self.prefix = [f'{prefix}'], f'/{prefix}'
        self.service = Service
        self.languages = settings.LANGUAGES
        self.response_model = Dict
        self.endpoint = self.single_method
        self.source = {'categories': (Category,),
                       'subcategories': (Subcategory, Category),
                       'countries': (Country,),
                       'regions': (Region, Country),
                       'subregions': (Subregion, Region, Country),
                       # 'customers': (Customer,),
                       'superfoods': (Superfood,),
                       'foods': (Food, Superfood),
                       'varietals': (Varietal,), }
        self.fields_name = ('name', 'description')

        self.router = APIRouter(prefix=self.prefix,
                                tags=self.tags,
                                dependencies=[Depends(get_active_user_or_internal)])
        self._setup_routes_()

    def _setup_routes_(self):
        for prefix, tag, function in self.__source_generator__(self.source, self.languages):
            self.router.add_api_route(prefix + '/{id}',
                                      endpoint=function, methods=["GET"],
                                      response_model=self.response_model)

    def __get_prepaire__(self, key: str, source: tuple, lang: str) -> tuple:
        """
        конвертирует (model, model1, model2), lang в
        prefix, tag, service.function, model, supermodel, superiormodel, lang
        """
        return (f'/{key}/{lang}', [f'{key}_{lang}'], self.endpoint)

    def __source_generator__(self, source: dict, langs: list):
        """
        генератор для создания роутов
        """
        return (self.__get_prepaire__(key, val, lang) for key, val in source.items() for lang in langs)
        # if len(val)
        # == 1)

    def __path_decoder__(self, path: str, tier: int = 3):
        """ декодирует url.path справа"""
        result = path.rsplit('/', tier)
        lang = result[-2]
        mod = result[-3]
        return mod, lang

    async def single_method(self, request: Request, id: int, session: AsyncSession = Depends(get_db)):
        current_path = request.url.path
        mod, lang = self.__path_decoder__(current_path)
        args = self.source.get(mod)
        result = await self.service.get_non_orm(session, models=args,
                                                fields_name=self.fields_name,
                                                lang=get_lang_prefix(lang),
                                                id=id)
        # result = await self.service.get_single_name_description(session, **kwargs)
        if not result:
            raise HTTPException(status_code=404, detail=f'record {id} not found')
        return result

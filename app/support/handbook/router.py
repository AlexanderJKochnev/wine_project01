# app/support/handbook/router.py
"""
    роутер для справочников
    выводит только словари  id: name
    по языкам
"""
from typing import Dict

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_active_user_or_internal
from app.core.config.database.db_async import get_db
from app.core.config.project_config import settings
from app.core.services.service import Service
from app.support import (Category, Country, Food, Region, Subcategory, Subregion, Superfood, Varietal)


class HandbookRouter:
    def __init__(self):
        prefix = settings.HANDBOOKS_PREFIX
        self.tags, self.prefix = [f'{prefix}'], f'/{prefix}'
        self.service = Service
        self.languages = settings.LANGUAGES
        self.response_model = Dict[int, str]
        self.endpoint: dict = {1: self.single_method,
                               2: self.pair_method,
                               3: self.triple_method}
        self.source = {'categories': (Category,),
                       'subcategories': (Subcategory, Category),
                       'countries': (Country,),
                       'regions': (Region, Country),
                       'subregions': (Subregion, Region, Country),
                       # 'customers': (Customer,),
                       'superfoods': (Superfood, ),
                       'foods': (Food, Superfood),
                       'varietal': (Varietal,),
                       }

        self.router = APIRouter(prefix=self.prefix,
                                tags=self.tags,
                                dependencies=[Depends(get_active_user_or_internal)])
        self._setup_routes_()

    def _setup_routes_(self):
        for prefix, tag, function in self.__source_generator__(self.source, self.languages):
            print(f'{prefix=}', self.languages)
            self.router.add_api_route(prefix,
                                      endpoint=function, methods=["GET"],
                                      response_model=self.response_model)

    def __get_prepaire__(self, key: str, source: tuple, lang: str) -> tuple:
        """
        конвертирует (model, model1, model2), lang в
        prefix, tag, service.function, model, supermodel, superiormodel, lang
        """
        return (f'/{key}/{lang}', [f'{key}_{lang}'], self.endpoint.get(len(source)))

    def __source_generator__(self, source: dict, langs: list):
        """
        генератор для создания роутов
        """
        return (self.__get_prepaire__(key, val, lang) for key, val in source.items() for lang in langs)

    def __path_decoder__(self, path: str, tier: int = 2):
        """ декодирует url.path справа"""
        result = path.rsplit('/', tier)
        print(f'path_decoder_result {result}')
        lang = result[-1]
        mod = result[-2]
        print(f'path_decoder_result {result}, {lang=}, {mod=}')
        return mod, lang

    async def single_method(self, request: Request, session: AsyncSession = Depends(get_db)):
        current_path = request.url.path
        mod, lang = self.__path_decoder__(current_path)
        args = self.source.get(mod)
        suffix = f'_{lang}' if lang != 'en' else ''
        return await self.service.get_single_name(session, *args, suffix)

    async def pair_method(self, request: Request, session: AsyncSession = Depends(get_db)):
        current_path = request.url.path
        mod, lang = self.__path_decoder__(current_path)
        args = self.source.get(mod)
        suffix = f'_{lang}' if lang != 'en' else ''
        return await self.service.get_pair_name(session, *args, suffix)

    async def triple_method(self, request: Request, session: AsyncSession = Depends(get_db)):
        current_path = request.url.path
        mod, lang = self.__path_decoder__(current_path)
        args = self.source.get(mod)
        suffix = f'_{lang}' if lang != 'en' else ''
        return await self.service.get_triple_name(session, *args, suffix)

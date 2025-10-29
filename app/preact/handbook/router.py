# app/support/handbook/router.py
"""
    роутер для справочников
    выводит только словари  id: name
    по языкам
"""
from typing import Dict

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Type, List
from app.core.models.base_model import DeclarativeBase
from app.core.utils.pydantic_utils import pyschema_helper
from app.core.utils.alchemy_utils import get_lang_prefix
from app.auth.dependencies import get_active_user_or_internal
from app.core.config.database.db_async import get_db
from app.core.config.project_config import settings
from app.core.services.service import Service
from app.core.repositories.sqlalchemy_repository import Repository
from app.support import (Category, Country, Food, Region, Subcategory, Subregion, Superfood, Varietal)


class HandbookRouter:
    def __init__(self):
        prefix = settings.HANDBOOKS_PREFIX
        self.tags, self.prefix = [f'{prefix}'], f'/{prefix}'
        self.service = Service
        self.repo = Repository
        self.languages = settings.LANGUAGES  # ['en', 'ru', 'fr', ...]
        # source {prefix: (Model, Name of PydanticModel without lang prefix
        # example {'subcategories': (Subcategory, 'SubcategoryView')}
        self.source = {'categories': Category,
                       'subcategories': Subcategory,
                       'countries': Country,
                       # 'regions': (Region, Country),
                       # 'subregions': (Subregion, Region, Country),
                       # 'customers': (Customer,),
                       'superfoods': Superfood,
                       # 'foods': (Food, Superfood),
                       'varietals': Varietal,
                       }
        self.router = APIRouter(prefix=self.prefix,
                                tags=self.tags,
                                dependencies=[Depends(get_active_user_or_internal)])
        self._setup_routes_()

    def _setup_routes_(self):
        for prefix, response_model in self.__source_generator__(self.source, self.languages):
            self.router.add_api_route(prefix, endpoint=self.get_list_view, methods=["GET"],
                                      response_model=response_model)

    def __get_prepaire__(self, key: str, model: Type[DeclarativeBase], lang: str) -> tuple:
        """
        get the prefix & responsible pydantic model
        :param key:     self.source.key
        :param model:  self.source.value
        :param lang:    one item from self.languages
        :return:        (prefix, response_model)
        """
        prefix = f'/{key}/{lang}'
        response_model = List[pyschema_helper(model, 'list', lang)]
        return (prefix, response_model)

    def __source_generator__(self, source: dict, langs: list):
        """
        генератор для создания роутов
        """
        return (self.__get_prepaire__(key, val, lang) for key, val in source.items() for lang in langs)

    def __path_decoder__(self, path: str, tier: int = 2):
        """ декодирует url.path справа"""
        result = path.rsplit('/', tier)
        lang = result[-1]   # язык 'en', 'ru', 'fr' ...
        mod = result[-2]    # self.source.key
        return mod, lang

    async def get_list_view(self, request: Request, session: AsyncSession = Depends(get_db)):
        current_path = request.url.path
        route = request.scope["route"]
        print(f'{route.response_model=}')
        # response_model = route.response_model
        pref, lang = self.__path_decoder__(current_path)
        model = self.source.get(pref)
        lang = get_lang_prefix(lang)  # convert lang to lang pref 'en' -> '', 'ru' -> '_ru' ...
        rows = await self.service.get_list_view(self.repo, model, session)
        return rows

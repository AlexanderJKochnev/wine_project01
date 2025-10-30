# app/preact/core/router.py
"""
    базовый роутер для preact

"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Type, List
from app.core.models.base_model import DeclarativeBase
from app.core.utils.pydantic_utils import get_repo, get_service
from app.core.utils.pydantic_utils import pyschema_helper
from app.core.utils.alchemy_utils import get_lang_prefix
from app.auth.dependencies import get_active_user_or_internal
from app.core.config.database.db_async import get_db
from app.core.config.project_config import settings
from app.support import (Category, Country, Food, Region, Subcategory, Subregion, Superfood, Varietal)
from app.core.repositories.sqlalchemy_repository import Repository
from app.core.services.service import Service


class PreactRouter:
    def __init__(self, prefix: str, method: str = 'GET', tier: int = 2):
        # prefix = settings.HANDBOOKS_PREFIX
        self.tags, self.prefix = [f'{prefix}'], f'/{prefix}'
        self.languages = settings.LANGUAGES  # ['en', 'ru', 'fr', ...]
        self.tier = tier  # применяется в _path_decoder-
        self.method = method
        self.source = {'categories': Category,
                       'subcategories': Subcategory,
                       'countries': Country,
                       'regions': Region,
                       'subregions': Subregion,
                       'superfoods': Superfood,
                       'foods': Food,
                       'varietals': Varietal,
                       }
        self.router = APIRouter(prefix=self.prefix,
                                tags=self.tags,
                                dependencies=[Depends(get_active_user_or_internal)])
        self.schemas_generator(self.source)
        self._setup_routes_()

    def schemas_generator(self, source: dict, *args, **kwargs):
        """ генератор pydantic схем - overrride """
        pass

    def get_lang_prefix(self, lang: str):
        return get_lang_prefix(lang)

    def get_repo(self, model: Type[DeclarativeBase]) -> Type[Repository]:
        return get_repo(model)

    def get_service(self, model: Type[DeclarativeBase]) -> Type[Service]:
        return get_service(model)

    def _setup_routes_(self):
        for prefix, response_model in self.__source_generator__(self.source, self.languages):
            self.router.add_api_route(prefix, endpoint=self.endpoint, methods=[self.method],
                                      response_model=response_model)

    def __get_prepaire__(self, key: str, model: Type[DeclarativeBase], lang: str) -> tuple:
        """
        override it?
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
        lang = result[1 - tier]   # язык 'en', 'ru', 'fr' ...
        mod = result[0 - tier]    # self.source.key
        return mod, lang

    async def endpoint(self, request: Request, session: AsyncSession = Depends(get_db)):
        """ override it """
        current_path = request.url.path
        route = request.scope["route"]
        # response_model = route.response_model
        pref, lang = self.__path_decoder__(current_path, self.tier)
        model = self.source.get(pref)
        lang = get_lang_prefix(lang)  # convert lang to lang pref 'en' -> '', 'ru' -> '_ru' ...
        repo = get_repo(model)
        service = get_service(model)
        print(f'{route.response_model=}, {repo=}')
        # rows = await self.service.get_list_view(repo, model, session)
        rows = await service.get_nodate(repo, model, session)
        return rows

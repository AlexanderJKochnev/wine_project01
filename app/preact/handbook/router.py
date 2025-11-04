# app/support/handbook/router.py
"""
    роутер для справочников
    выводит только словари  id: name
    по языкам
"""
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.preact.core.router import PreactRouter
from app.core.config.database.db_async import get_db
from typing import List, Type
from app.core.schemas.base import ListView
from app.core.models.base_model import DeclarativeBase


class HandbookRouter(PreactRouter):
    def __init__(self):
        super().__init__(prefix='handbooks', method='GET', tier=2)

    def __get_prepaire__(self, key: str, model: Type[DeclarativeBase]) -> tuple:
        """
        get the prefix & responsible pydantic model
        :param key:     self.source.key
        :param model:  self.source.value
        :param lang:    one item from self.languages
        :return:        (prefix, response_model)
        """
        prefix = f'/{key}'
        # response_model = List[get_pyschema(model, 'View')]
        response_model = List[ListView]
        return (prefix, response_model)

    async def endpoint(self, request: Request, lang: str, session: AsyncSession = Depends(get_db)):
        current_path = request.url.path
        route = request.scope["route"]
        # response_model = route.response_model
        pref, _ = self.__path_decoder__(current_path)
        model = self.source.get(pref)
        lang = self.get_lang_prefix(lang)  # convert lang to lang pref 'en' -> '', 'ru' -> '_ru' ...
        repo = self.get_repo(model)
        service = self.get_service(model)
        print(f'{route.response_model=}, {repo=}')
        rows = await service.get_nodate(repo, model, session)
        return rows

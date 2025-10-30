# app/support/handbook/router.py
"""
    роутер для ListView для всех кроме Drink & Items
    выводит только словари  id: name
    по языкам
"""
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.preact.core.router import PreactRouter
from app.core.config.database.db_async import get_db
from typing import Type
from app.core.utils.pydantic_utils import pyschema_helper
from app.core.models.base_model import DeclarativeBase


class GetRouter(PreactRouter):
    def __init__(self):
        super().__init__(prefix='get', method='GET', tier=3)

    def __get_prepaire__(self, key: str, model: Type[DeclarativeBase], lang: str) -> tuple:
        """
        get the prefix & responsible pydantic model
        :param key:     self.source.key
        :param model:  self.source.value
        :param lang:    one item from self.languages
        :return:        (prefix, response_model)
        """
        prefix = f'/{key}/{lang}' + '/{id}'
        pyschema = pyschema_helper(model, 'single', lang)
        response_model = pyschema
        return (prefix, response_model)

    async def endpoint(self, request: Request, id: int, session: AsyncSession = Depends(get_db)):
        current_path = request.url.path
        # route = request.scope["route"]
        # response_model = route.response_model
        pref, lang = self.__path_decoder__(current_path, 3)
        model = self.source.get(pref)
        lang = self.get_lang_prefix(lang)  # convert lang to lang pref 'en' -> '', 'ru' -> '_ru' ...
        repo = self.get_repo(model)
        service = self.get_service(model)
        instance = await service.get_by_id(id, repo, model, session)
        return instance

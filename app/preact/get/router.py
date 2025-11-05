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
from app.core.utils.pydantic_utils import get_pyschema


class GetRouter(PreactRouter):
    def __init__(self):
        super().__init__(prefix='get', method='GET', tier=3)

    def __source_generator__(self, source: dict):
        """
        генератор для создания роутов
        """
        return ((f'/{key}' + '/{lang}/{id}', get_pyschema(val, 'DetailView')) for key, val in source.items())

    async def endpoint(self, request: Request, lang: str, id: int, session: AsyncSession = Depends(get_db)):
        current_path = request.url.path
        # route = request.scope["route"]
        # response_model = route.response_model
        pref, lang = self.__path_decoder__(current_path, 3)
        model = self.source.get(pref)
        repo = self.get_repo(model)
        service = self.get_service(model)
        obj = await service.get_detail_view(lang, id, repo, model, session)
        return obj

# app/support/read/router.py
"""
    роутер для UpdateView (заполнение) для всех кроме Drink & Items
"""
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.preact.core.router import PreactRouter
from app.core.config.database.db_async import get_db
from app.core.utils.pydantic_utils import get_pyschema


class ReadRouter(PreactRouter):
    def __init__(self):
        super().__init__(prefix='read', method='GET', tier=2)

    def __source_generator__(self, source: dict):
        """
        генератор для создания роутов
        """
        return ((f'/{key}' + '/{id}', get_pyschema(val, 'Create')) for key, val in source.items())

    async def endpoint(self, request: Request, id: int, session: AsyncSession = Depends(get_db)):
        current_path = request.url.path
        # route = request.scope["route"]
        # response_model = route.response_model
        pref, lang = self.__path_decoder__(current_path, 2)
        model = self.source.get(pref)
        repo = self.get_repo(model)
        service = self.get_service(model)
        obj = await service.get_by_id(id, repo, model, session)
        return obj

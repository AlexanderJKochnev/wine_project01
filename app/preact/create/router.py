# app/preact/create/router.py
from typing import Any, Dict

from fastapi import Body, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.utils.pydantic_utils import sqlalchemy_to_pydantic_post
from app.core.config.database.db_async import get_db
from app.preact.core.router import PreactRouter


class CreateRouter(PreactRouter):
    def __init__(self):
        super().__init__(prefix='create', method='POST', tier=2)

    def __set_schema__(self, model):
        """ создает Create схему для response_model """
        setattr(self, f'{model.__name__}Create', sqlalchemy_to_pydantic_post(model))

    def __get_schemas__(self, model):
        """ получает ранее созданную Create схему """
        return getattr(self, f'{model.__name__}Create')

    def schemas_generator(self, source: dict):
        """ генератор pydantic схем """
        for model in self.source.values():
            self.__set_schema__(model)

    def __source_generator__(self, source: dict, langs: list):
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

    async def endpoint(self, request: Request, data: Dict[str, Any] = Body(...),
                       session: AsyncSession = Depends(get_db)):
        try:
            current_path = request.url.path
            tmp = self.__path_decoder__(current_path)
            model = self.source.get(tmp)
            schema = self.__get_schemas__(model)
            repo = self.get_repo(model)
            service = self.get_service(model)
            model_data = schema(**data)
            obj = await service.get_or_create(model_data, repo, model, session)
            return obj
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=505,
                detail=f'Create Fault, {e}'
            )

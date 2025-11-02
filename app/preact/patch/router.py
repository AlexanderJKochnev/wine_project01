# app/preact/path/router.py
from fastapi import Request, Depends, Body, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.preact.core.router import PreactRouter
from app.core.config.database.db_async import get_db
from typing import Dict, Any
from app.core.utils.pydantic_utils import pyschema_helper
# from app.core.models.base_model import DeclarativeBase


class PatchRouter(PreactRouter):
    def __init__(self):
        super().__init__(prefix='path', method='PATH', tier=3)

    def __set_schema__(self, model):
        """  находит  Update схему для response_model """
        setattr(self, f'{model.__name__}Update', pyschema_helper(model, 'update'))
        # setattr(self, f'{model.__name__}Update', sqlalchemy_to_pydantic_post(model))

    def __get_schemas__(self, model):
        """ получает ранее созданную Create схему """
        return getattr(self, f'{model.__name__}Update')

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
            # obj = await service.patch(id, model_data, repo, model, session)
            result = await service.patch(id, data, repo, model, session)
            print(result, '===============================')
            return result
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=505,
                detail=f'Update fault, {e}'
            )

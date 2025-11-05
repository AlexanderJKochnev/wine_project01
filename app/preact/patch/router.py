# app/preact/path/router.py
from fastapi import Request, Depends, Body, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.preact.core.router import PreactRouter
from app.core.config.database.db_async import get_db
from typing import Dict, Any
from app.core.utils.pydantic_utils import get_pyschema


class PatchRouter(PreactRouter):
    def __init__(self):
        super().__init__(prefix='patch', method='PATCH', tier=3)

    def __set_schema__(self, model):
        """  находит  Update схему для response_model """
        schema = get_pyschema(model, 'Update')  # or sqlalchemy_to_pydantic_post(model)
        setattr(self, f'{model.__name__}Create', schema)

    def __get_schemas__(self, model):
        """ получает ранее созданную Create схему """
        return getattr(self, f'{model.__name__}Update')

    def schemas_generator(self, source: dict):
        """ генератор pydantic схем """
        for model in self.source.values():
            self.__set_schema__(model)

    def __source_generator__(self, source: dict):
        """
        генератор для создания роутов
        """
        return ((f'/{key}' + '/{id}', get_pyschema(val, 'Update')) for key, val in source.items())

    async def endpoint(self, request: Request, id: int, data: Dict[str, Any] = Body(...),
                       session: AsyncSession = Depends(get_db)):
        try:
            current_path = request.url.path
            _, tmp = self.__path_decoder__(current_path, self.tier)
            model = self.source.get(tmp)
            route = request.scope["route"]
            schema = route.response_model
            repo = self.get_repo(model)
            service = self.get_service(model)
            model_data = schema(**data)
            result = await service.patch(id, model_data, repo, model, session)
            return result
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=505,
                detail=f'Update fault, {e}'
            )

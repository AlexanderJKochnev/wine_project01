# app/preact/delete/router.py

from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_active_user_or_internal
from app.core.config.database.db_async import get_db
from app.core.repositories.sqlalchemy_repository import Repository
from app.core.schemas.base import DeleteResponse
from app.core.services.service import Service
from app.support import (Category, Country, Food, Region, Subcategory, Subregion, Superfood, Varietal)


class DeleteRouter:
    def __init__(self):
        prefix = 'delete'
        self.tags, self.prefix = [f'{prefix}'], f'/{prefix}'
        self.service = Service
        self.repo = Repository
        self.response_model = DeleteResponse
        self.source = {'categories': Category,
                       'subcategories': Subcategory,
                       'countries': Country,
                       'regions': Region,
                       'subregions': Subregion,
                       # 'customers': Customer,
                       'superfoods': Superfood,
                       'foods': Food,
                       'varietals': Varietal}
        self.router = APIRouter(prefix=self.prefix, tags=self.tags,
                                dependencies=[Depends(get_active_user_or_internal)])
        self.setup_routes()

    def setup_routes(self):
        for prefix in self.source.keys():
            self.router.add_api_route(f'/{prefix}/' + '{id}',
                                      self.delete,
                                      methods=["DELETE"],
                                      response_model=self.response_model)

    def __path_decoder__(self, path: str, tier: int = 2):
        """ декодирует url.path справа"""
        result = path.rsplit('/')
        mod = result[-2]
        return mod

    async def delete(self, request: Request, id: int,
                     session: AsyncSession = Depends(get_db)) -> DeleteResponse:
        """
            Удаление одной записи по id
        """
        current_path = request.url.path
        tmp = self.__path_decoder__(current_path)
        model = self.source.get(tmp)
        existing_item = await self.service.get_by_id(id, self.repo, model, session)
        if not existing_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Запись отсутствует на сервере и не может быть удалена")
        result = await self.service.delete(existing_item, self.repo, session)
        resu = {'success': result, 'deleted_count': 1 if result else 0,
                'message': f'{model.__name__} with id {id} has been deleted'}
        return DeleteResponse(**resu)

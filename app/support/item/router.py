# app/support/item/router.py
import json
from typing import Optional

from fastapi import Depends, File, Form, HTTPException, Query, status, UploadFile
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.database.db_async import get_db
from app.core.config.project_config import get_paging
from app.core.routers.base import BaseRouter
from app.core.schemas.base import PaginatedResponse
from app.mongodb.service import ImageService
from app.support.item.model import Item
from app.support.item.repository import ItemRepository
from app.support.item.schemas import (ItemCreate, ItemCreateRelation, ItemCreateResponseSchema, ItemUpdate)

paging = get_paging


class ItemRouter(BaseRouter):
    def __init__(self, prefix: str = '/items', **kwargs):
        super().__init__(
            model=Item,
            prefix=prefix,
            repo=ItemRepository
        )
        self.image_service: ImageService = Depends()

    def setup_routes(self):
        super().setup_routes()
        self.router.add_api_route(
            "/full", self.create_relation_image, status_code=status.HTTP_200_OK, methods=["POST"],
            response_model=self.read_schema
        )
        """ import from upload directory """
        self.router.add_api_route(
            "/direct", self.direct_import_data, status_code=status.HTTP_200_OK, methods=["POST"],
            response_model=dict)
        self.router.add_api_route(
            "/direct/{id}", self.direct_import_single_data, status_code=status.HTTP_200_OK, methods=["GET"],
            response_model=dict
        )

    async def create(self, data: ItemCreate,
                     session: AsyncSession = Depends(get_db)) -> ItemCreateResponseSchema:
        return await super().create(data, session)

    async def patch(self, id: int, data: ItemUpdate,
                    session: AsyncSession = Depends(get_db)) -> ItemCreateResponseSchema:
        return await super().patch(id, data, session)

    async def create_relation(self, data: ItemCreateRelation,
                              session: AsyncSession = Depends(get_db)) -> ItemCreateResponseSchema:
        result = await super().create_relation(data, session)
        return result

    async def direct_import_data(self,
                                 session: AsyncSession = Depends(get_db),
                                 image_service: ImageService = Depends()) -> dict:
        """
        Импорт записей с зависимостями. Для того что бы выполнить импорт нужно
        на сервере поместить файл data.json в директорию UPLOAD_DIR, в ту же директорию разместить файлы с
        изображениями.
        - если в таблице есть зависимости они будут рекурсивно найдены в связанных таблицах (или добавлены при
        отсутсвии), кроме того будет добавлено изображение по его имени (перед этим выполнить импорт изображений
        /mongodb/images/direct.
        операция длительная - наберитесь терпения
        """
        try:
            result = await self.service.direct_upload(session, image_service)
            """
            {'total_input': n,
             'count of added records': n - len(error_list),
             'error': error_list,
             'error_nmbr': len(error_list)}
            """
            return result
        except Exception as e:
            raise HTTPException(status_code=422, detail=e)

    async def create_relation_image(self,
                                    data: str = Form(..., description="JSON string of DrinkCreateRelation"),
                                    file: UploadFile = File(...),
                                    session: AsyncSession = Depends(get_db),
                                    image_service: ImageService = Depends()
                                    ) -> ItemCreateResponseSchema:
        """
        Создание одной записи с зависимостями - если в таблице есть зависимости
        они будут рекурсивно найдены в связанных таблицах (или добавлены при отсутсвии),
        кроме того будет добавлено изображение.
        перед этим нужно импортировать изображения
        POST mongodb/images/direct
        """
        try:
            data_dict = json.loads(data)
            item_data = ItemCreateRelation(**data_dict)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=422, detail=f"Invalid JSON: {e}")
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=e.errors())
        # load image to database, get image_id & image_path
        # image_id, image_path = await image_service.upload_image(file, description=item_data.drink.title)
        # item_data.image_path = image_path
        # item_data.image_id = image_id
        result = await super().create_relation(item_data, session)
        return result

    async def direct_import_single_data(self, id: str,
                                        session: AsyncSession = Depends(get_db),
                                        image_service: ImageService = Depends()) -> dict:
        """
        Импорт записей с зависимостями. Для того что бы выполнить импорт нужно
        на сервере поместить файл data.json в директорию UPLOAD_DIR, в ту же директорию разместить файлы с
        изображениями.
        - если в таблице есть зависимости они будут рекурсивно найдены в связанных таблицах (или добавлены при
        отсутсвии), кроме того будет добавлено изображение по его имени (перед этим выполнить импорт изображений
        /mongodb/images/direct.
        операция длительная - наберитесь терпения
        """
        try:
            id = id.strop('.png')
            result = await self.service.direct_single_upload(id, session)
            # if result.get('error_nmbr', 0) > 0:
            #     raise HTTPException(status_code=423, detail=result)
            return result
        except Exception as e:
            raise HTTPException(status_code=422, detail=e)

    async def search(self,
                     search: Optional[str] = None,
                     country_enum: Optional[str] = None,
                     category_enum: Optional[str] = None,
                     page: int = Query(1, ge=1),
                     page_size: int = Query(paging.get('def', 20),
                                            ge=paging.get('min', 1),
                                            le=paging.get('max', 1000)),
                     session: AsyncSession = Depends(get_db)) -> PaginatedResponse:
        """
            Поиск по всем текстовым полям основной таблицы
            с постраничным выводом результата
        """
        kwargs: str = {'page': page, 'page_size': page_size}
        if search:
            kwargs['search_str'] = search
        if country_enum:
            kwargs['country_enum'] = country_enum
        if category_enum:
            kwargs['category_enum'] = category_enum
        return await self.service.search(self.repo, self.model, session,
                                         **kwargs)

    async def search_all(self,
                         search: Optional[str] = None,
                         country_enum: Optional[str] = None,
                         category_enum: Optional[str] = None,
                         session: AsyncSession = Depends(get_db)) -> PaginatedResponse:
        """
            Поиск по всем текстовым полям основной таблицы
            с постраничным выводом результата
        """
        kwargs: str = {}
        if search:
            kwargs['search_str'] = search
        if country_enum:
            kwargs['country_enum'] = country_enum
        if category_enum:
            kwargs['category_enum'] = category_enum
        return await self.service.search(self.repo, self.model, session,
                                         **kwargs)

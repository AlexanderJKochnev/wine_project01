# app/support/item/router.py

from sqlalchemy.ext.asyncio import AsyncSession
import json
from pydantic import ValidationError
from fastapi import Depends, status, HTTPException, UploadFile, Form, File
from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.item.model import Item
from app.support.item.repository import ItemRepository
from app.support.item.schemas import (ItemRead, ItemCreate, ItemUpdate, ItemCreateRelations,
                                      ItemCreateResponseSchema)
from app.support.item.service import ItemService
from app.mongodb.service import ImageService


class ItemRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Item,
            repo=ItemRepository,
            create_schema=ItemCreate,
            read_schema=ItemRead,
            path_schema=ItemUpdate,
            prefix="/items",
            tags=["items"],
            create_response_schema=ItemCreateResponseSchema,
            create_schema_relation=ItemCreateRelations,
            service=ItemService
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

    async def create(self, data: ItemCreate,
                     session: AsyncSession = Depends(get_db)) -> ItemCreateResponseSchema:
        return await super().create(data, session)

    async def patch(self, id: int, data: ItemUpdate,
                    session: AsyncSession = Depends(get_db)) -> ItemCreateResponseSchema:
        return await super().patch(id, data, session)

    async def create_relation(self, data: ItemCreateRelations,
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
            result = await self.service.direct_upload(session)
            return result
        except Exception as e:
            raise HTTPException(status_code=422, detail=e)

    async def create_relation_image(self,
                                    data: str = Form(..., description="JSON string of DrinkCreateRelations"),
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
            item_data = ItemCreateRelations(**data_dict)
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

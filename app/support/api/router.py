# app/support/api/router.py
from dataclasses import dataclass
from datetime import datetime, timezone

from dateutil.relativedelta import relativedelta
from fastapi import Depends, Query

from app.core.config.project_config import settings
from app.mongodb import router as mongorouter
from app.mongodb.models import FileListResponse
from app.mongodb.service import ImageService
from app.support.drink.router import DrinkRouter


@dataclass
class Data:
    prefix: str
    delta: str
    # drink_paginated_response: Type[BaseModel]
    mongo: str
    drink: str


data = Data(prefix=settings.API_PREFIX,
            delta=(datetime.now(timezone.utc) - relativedelta(years=2)).isoformat(),
            mongo='mongo',
            drink='drink'
            )


class ApiRouter(DrinkRouter):
    def __init__(self):
        super().__init__(prefix='/api', tags=['api'])
        self.prefix = data.prefix
        self.tags = data.prefix

    def setup_routes(self):
        self.router.add_api_route("", self.get, methods=["GET"], response_model=self.paginated_response)
        self.router.add_api_route(f"/{data.mongo}", self.get_images_after_date, response_model=FileListResponse)
        self.router.add_api_route(f"/{data.mongo}" + "/{id}", self.download_image)

    async def get_images_after_date(self, after_date: datetime = Query(data.delta, description="Дата в формате ISO "
                                                                                               "8601 (например, "
                                                                                               "2024-01-01T00:00:00Z)"),
                                    page: int = Query(1, ge=1, description="Номер страницы"),
                                    per_page: int = Query(100, ge=1, le=1000,
                                                          description="Количество элементов на странице"),
                                    image_service: ImageService = Depends()
                                    ):
        """
        Получение списка изображений, созданных после заданной даты (по умолчанию за два года до нстоящего времени)
        """
        return await mongorouter.get_images_after_date(after_date, page, per_page, image_service)

    async def download_image(self, file_id: str, image_service: ImageService = Depends()):
        """
            Получение одного изображения по _id
        """
        return await mongorouter.download_image(file_id, image_service)

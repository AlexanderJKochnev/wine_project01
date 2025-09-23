# app/support/drink/router.py
from fastapi import Depends, status, UploadFile, File, HTTPException, Form
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
import json
from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.drink.drink_food_repo import DrinkFoodRepository
from app.support.drink.drink_food_service import DrinkFoodService
from app.support.drink.model import Drink
from app.support.drink.repository import DrinkRepository
from app.support.drink.schemas import (DrinkCreate, DrinkCreateResponseSchema, DrinkRead,
                                       DrinkCreateRelationsWithImage,
                                       DrinkUpdate, DrinkFoodLinkUpdate, DrinkCreateRelations)
from app.support.drink.service import DrinkService
from app.mongodb.models import ImageCreate
from app.mongodb.service import ImageService


class DrinkRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Drink,
            repo=DrinkRepository,
            create_schema=DrinkCreate,
            read_schema=DrinkRead,
            create_schema_relation=DrinkCreateRelations,
            create_response_schema=DrinkCreateResponseSchema,
            path_schema=DrinkUpdate,
            prefix="/drinks",
            tags=["drinks"],
            service=DrinkService
        )
        self.create_relation_image = DrinkCreateRelationsWithImage
        # self.image_service=ImageService
        # self.create_response_schema = DrinkCreateResponseSchema

    def setup_routes(self):
        super().setup_routes()
        self.router.add_api_route("/full",
                                  self.create_relation_image,
                                  status_code=status.HTTP_200_OK,
                                  methods=["POST"],
                                  response_model=dict)
        # то что ниже удалить - было нужно до relation
        self.router.add_api_route("/{id}/foods", self.update_drink_foods,
                                  methods=["PATCH"])

    def get_drink_food_service(session: AsyncSession) -> DrinkFoodService:
        repo = DrinkFoodRepository(session)
        return DrinkFoodService(repo)

    async def update_drink_foods(self, id: int,
                                 data: DrinkFoodLinkUpdate,
                                 session: AsyncSession = Depends(get_db)):
        """ обновление many to many """
        service = self.get_drink_food_service(session)
        await service.set_drink_foods(id, data.food_ids)
        return {"status": "success"}

    async def create(self, data: DrinkCreate, session: AsyncSession = Depends(get_db)) -> DrinkCreateResponseSchema:
        result = await super().create(data, session)
        return result

    async def create_relation(self, data: DrinkCreateRelations,
                              session: AsyncSession = Depends(get_db)) -> DrinkRead:
        result = await super().create_relation(data, session)
        return result

    async def patch(self, id: int, data: DrinkUpdate,
                    session: AsyncSession = Depends(get_db)) -> DrinkRead:
        return await super().patch(id, data, session)

    async def create_relation_image(self,
                                    data: str = Form(..., description="JSON string of DrinkCreateRelations"),
                                    file: UploadFile = File(...),
                                    session: AsyncSession = Depends(get_db),
                                    image_service: ImageService = Depends()
                                    ) -> DrinkRead:
        try:
            data_dict = json.loads(data)
            drink_data = DrinkCreateRelations(**data_dict)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=422, detail=f"Invalid JSON: {e}")
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=e.errors())
        # title = data.title
        # content = await file.read()
        # file_id = await image_service.upload_image(file.filename, content, title, 1)
        # data.image_path = file_id
        # return {"id": file_id, "message": "Image uploaded successfully"}
        result = await super().create_relation(drink_data, session)
        return result

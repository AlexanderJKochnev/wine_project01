# app/support/drink/router.py
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, UploadFile, File, Form
from typing import Optional
from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.drink.model import Drink
from app.support.drink.repository import DrinkRepository
from app.support.drink.schemas import DrinkRead, DrinkCreate, DrinkUpdate


class DrinkRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Drink,
            repo=DrinkRepository,
            create_schema=DrinkCreate,
            update_schema=DrinkUpdate,
            read_schema=DrinkRead,
            prefix="/drinks",
            tags=["drinks"]
        )
        self.setup_routes()

    async def create(self, data: DrinkCreate, session: AsyncSession = Depends(get_db)) -> DrinkRead:
        return await super().create(data, session)

    async def update(self, id: int, data: DrinkUpdate,
                     session: AsyncSession = Depends(get_db)) -> DrinkRead:
        return await super().update(id, data, session)

    async def create_with_image(
        self,
        name: str = Form(...),
        subtitle: Optional[str] = Form(None),
        alcohol: Optional[float] = Form(None),
        sugar: Optional[float] = Form(None),
        aging: Optional[int] = Form(None),
        sparkling: Optional[bool] = Form(None),
        category_id: int = Form(...),
        food_id: Optional[int] = Form(None),
        region_id: int = Form(...),
        color_id: Optional[int] = Form(None),
        sweetness_id: Optional[int] = Form(None),
        image_file: Optional[UploadFile] = File(None),
        session: AsyncSession = Depends(get_db)
    ) -> DrinkRead:
        data = {"name": name,
                "subtitle": subtitle,
                "alcohol": alcohol,
                "sugar": sugar,
                "aging": aging,
                "sparkling": sparkling,
                "category_id": category_id,
                "food_id": food_id,
                "region_id": region_id,
                "color_id": color_id,
                "sweetness_id": sweetness_id,
                "image_file": image_file}
        return await super().create_with_image(session=session, **data)

    async def update_with_image(
        self,
        id: int,
        name: Optional[str] = Form(None),
        subtitle: Optional[str] = Form(None),
        alcohol: Optional[float] = Form(None),
        sugar: Optional[float] = Form(None),
        aging: Optional[int] = Form(None),
        sparkling: Optional[bool] = Form(None),
        category_id: Optional[int] = Form(None),
        food_id: Optional[int] = Form(None),
        region_id: Optional[int] = Form(None),
        color_id: Optional[int] = Form(None),
        sweetness_id: Optional[int] = Form(None),
        image_file: Optional[UploadFile] = File(None),
        remove_image: Optional[bool] = Form(False),
        session: AsyncSession = Depends(get_db)
    ) -> DrinkRead:
        data = {}
        if name is not None:
            data["name"] = name
        if subtitle is not None:
            data["subtitle"] = subtitle
        if alcohol is not None:
            data["alcohol"] = alcohol
        if sugar is not None:
            data["sugar"] = sugar
        if aging is not None:
            data["aging"] = aging
        if sparkling is not None:
            data["sparkling"] = sparkling
        if category_id is not None:
            data["category_id"] = category_id
        if food_id is not None:
            data["food_id"] = food_id
        if region_id is not None:
            data["region_id"] = region_id
        if color_id is not None:
            data["color_id"] = color_id
        if sweetness_id is not None:
            data["sweetness_id"] = sweetness_id

        # Обработка изображения
        if remove_image:
            data["image_file"] = None
        elif image_file:
            data["image_file"] = image_file

        return await super().update_with_image(id=id, session=session, **data)


router = DrinkRouter().router

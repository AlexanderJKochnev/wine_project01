# app/admin/sqladmin.md
from sqladmin import ModelView
from sqlalchemy.orm import selectinload
from sqlalchemy import select, delete
from typing import List, Any
import asyncio

from sqlalchemy.orm import selectinload
from sqlalchemy import select, delete
from app.admin.core import AutoModelView, BaseAdmin
# --------подключение моделей-----------
from app.support.drink.model import Drink, DrinkFood
from app.support.category.model import Category
from app.support.country.model import Country
from app.support.customer.model import Customer
from app.support.warehouse.model import Warehouse
from app.support.food.model import Food
from app.support.item.model import Item
from app.support.region.model import Region
from app.support.color.model import Color
from app.support.sweetness.model import Sweetness
from app.support.subregion.model import Subregion


class DrinkAdmin(AutoModelView, BaseAdmin, model=Drink):
    form_ajax_refs = {'foods':
                          {'fields': ('name',), 'order_by': 'name', 'widget': 'checkbox'  # Это ключевой параметр!
            }}

    async def on_model_change(self, data, model, is_created):
        # Сохраняем основную модель сначала
        await super().on_model_change(data, model, is_created)
        
        # Обрабатываем связи many-to-many
        if 'foods' in data:
            food_ids = [int(food_id) for food_id in data['foods']]
            
            # Удаляем старые связи
            await self.session.execute(
                    delete(DrinkFood).where(DrinkFood.drink_id == model.id)
                    )
            
            # Добавляем новые связи
            for food_id in food_ids:
                self.session.add(DrinkFood(drink_id = model.id, food_id = food_id))
            
            await self.session.commit()
    
    async def on_model_delete(self, model):
        # Удаляем связи перед удалением напитка
        await self.session.execute(
                delete(DrinkFood).where(DrinkFood.drink_id == model.id)
                )
        await super().on_model_delete(model)
    
    async def get_one_form(self, obj):
        # Загружаем объект с привязанными food
        stmt = select(Drink).where(Drink.id == obj.id).options(selectinload(Drink.foods))
        result = await self.session.execute(stmt)
        drink = result.scalar_one()
        
        return {"name": drink.name, "subtitle": drink.subtitle, "alcohol": drink.alcohol,
                "foods": [str(food.id) for food in drink.foods]  # список ID для чекбоксов
                }


class CategoryAdmin(AutoModelView, BaseAdmin, model=Category):
    name = "Category"
    name_plural = "Categories"


class CountryAdmin(AutoModelView, BaseAdmin, model=Country):
    name = 'Country'
    name_plural = 'Countries'


class CustomerAdmin(AutoModelView, BaseAdmin, model=Customer):
    pass


class WarehouseAdmin(AutoModelView, BaseAdmin, model=Warehouse):
    pass


class FoodAdmin(AutoModelView, BaseAdmin, model=Food):
    pass


class ItemAdmin(AutoModelView, BaseAdmin, model=Item):
    pass


class RegionAdmin(AutoModelView, BaseAdmin, model=Region):
    pass


class SubregionAdmin(AutoModelView, BaseAdmin, model=Subregion):
    pass


class SweetnessAdmin(AutoModelView, BaseAdmin, model=Sweetness):
    name = 'Sweetness'
    name_plural = 'Sweetness type'


class ColorAdmin(AutoModelView, BaseAdmin, model=Color):
    pass


"""class FileAdmin(ModelView, model=File):
    column_list = [File.id, File.filename, File.size]
    form_excluded_columns = [File.seaweedfs_id]  # не редактируем вручную

    async def after_model_change(self, model: File,
                                 is_created: bool,
                                 request: Request,
                                 session: AsyncSession = Depends(get_db)) -> None:
        if "file" in (await request.form()):
            form_data = await request.form()
            file_id = str(uuid.uuid4())
            file = form_data["file"]
            if isinstance(file, UploadFile) and file.filename:
                # content = await file.read()
                # model.seaweedfs_id = str(uuid.uuid4())
                model = FileCreate(filename=file.filename,
                                   content_type=file.content_type,
                                   size=await file.seek(0, 2) or 0,
                                   seaweedfs_id=file_id)
                await seaweed.upload(file, model.seaweedfs_id)
                # Асинхронное сохранение в БД
                session.add(model)
                await session.commit()
                await session.refresh(model)

    async def after_model_delete(self, model: File, request: Request) -> None:
        await seaweed.delete(model.seaweedfs_id)

"""

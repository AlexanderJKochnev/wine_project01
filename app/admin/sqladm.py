# app/admin/sqladmin.md
# from wtforms.widgets import TextArea
from app.admin.core import AutoModelView, ModelView
from fastapi import Request, UploadFile, Depends, HTTPException
from fastapi import UploadFile as FastAPIUploadFile
# from starlette.responses import RedirectResponse
from app.core.config.database.db_sync import get_db_sync  # синхронная сессия
from sqlalchemy.ext.asyncio import AsyncSession
# from app.core.config.database.db_async import get_db
from app.support.file.service import SeaweedFSClient
import uuid
# from app.support.file.schemas import FileCreate
# --------подключение моделей-----------
from app.support.drink.model import Drink
from app.support.category.model import Category
from app.support.country.model import Country
from app.support.customer.model import Customer
from app.support.warehouse.model import Warehouse
from app.support.food.model import Food
from app.support.item.model import Item
from app.support.region.model import Region
from app.support.color.model import Color
from app.support.sweetness.model import Sweetness
from app.support.file.model import File
import io

seaweed = SeaweedFSClient()
print("✅ FileAdmin loaded!")

class FileAdmin(ModelView, model=File):
    column_list = [File.id, File.filename, File.size, File.content_type]
    form_excluded_columns = [File.seaweedfs_id]  # не редактируем вручную
    form_template = "admin/file/form.html"  # ← указываем кастомный шаблон

    async def after_model_change(self, model: File, is_created: bool, request: Request) -> None:
        form = await request.form()
        if "upload_file" in form:
            upload_file = form["upload_file"]
            if hasattr(upload_file, "filename") and upload_file.filename:
                # Оборачиваем в FastAPI UploadFile
                file_stream = io.BytesIO(await upload_file.read())
                fastapi_file = FastAPIUploadFile(
                    file=file_stream,
                    filename=upload_file.filename,
                    content_type=upload_file.content_type or "application/octet-stream",
                )

                file_id = str(uuid.uuid4())
                try:
                    # Загружаем в SeaweedFS
                    result = await seaweed.upload(fastapi_file, file_id)

                    # Сохраняем метаданные
                    model.filename = fastapi_file.filename
                    model.content_type = fastapi_file.content_type
                    model.size = len(result.get("eTag", ""))  # или получите из ответа
                    model.seaweedfs_id = file_id

                    # Сохраняем в БД
                    sync_db = next(get_db_sync())
                    sync_db.add(model)
                    sync_db.commit()
                    sync_db.refresh(model)
                    sync_db.close()

                except Exception as e:
                    # При ошибке удаляем из SeaweedFS
                    await seaweed.delete(file_id)
                    raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    async def after_model_delete(self, model: File, request: Request) -> None:
        await seaweed.delete(model.seaweedfs_id)


class DrinkAdmin(AutoModelView, model=Drink):
    # column_searchable_list = [Drink.name, Drink.name_ru]
    # column_sortable_list = [Drink.id, Drink.name, Drink.category]
    # form_columns = [Drink.name, Drink.subtitle,
    #                 Drink.description, Drink.category]
    # form_excluded_columns = ['created_at', 'updated_at', 'pk']
    pass


class CategoryAdmin(AutoModelView, model=Category):
    name = "Category"
    name_plural = "Categories"


class CountryAdmin(AutoModelView, model=Country):
    name = 'Country'
    name_plural = 'Countries'


class CustomerAdmin(AutoModelView, model=Customer):
    pass


class WarehouseAdmin(AutoModelView, model=Warehouse):
    pass


class FoodAdmin(AutoModelView, model=Food):
    pass


class ItemAdmin(AutoModelView, model=Item):
    pass


class RegionAdmin(AutoModelView, model=Region):
    pass


class SweetnessAdmin(AutoModelView, model=Sweetness):
    name = 'Sweetness'
    name_plural = 'Sweetness type'


class ColorAdmin(AutoModelView, model=Color):
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

# app/admin/sqladmin.md
# from wtforms.widgets import TextArea
from app.admin.core import AutoModelView
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

# app/admin/sqladmin.md
from app.admin.core import AutoModelView, BaseAdmin
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


class DrinkAdmin(AutoModelView, BaseAdmin, model=Drink):
    """
    column_list = ['name']
    column_searchable_list = [Drink.name]
    column_sortable_list = [Drink.id, Drink.name, Drink.alcohol]
    column_labels = {
        Drink.name: "Название",
        "image_preview": "Изображение"
    }

    form_columns = [
        Drink.name, Drink.subtitle, Drink.alcohol, Drink.sugar,
        Drink.aging, Drink.sparkling, Drink.category_id, Drink.food_id,
        Drink.region_id, Drink.color_id, Drink.sweetness_id, "image_path"
    ]

    def get_list_value(self, model, column):
        if column.key == "image_preview":
            if model.image_path:
                return f'<img src="/images/{model.image_path}" style="max-width: 100px; max-height: 100px;" />'
            return "Нет изображения"
        return super().get_list_value(model, column)

    def get_detail_value(self, model, column):
        if column.key == "image_path" and model.image_path:
            return f'<img src="/images/{model.image_path}" style="max-width: 300px;" />'
        return super().get_detail_value(model, column)
    """
    # column_list = ['name', 'name_ru']
    # column_details_list =
    # form_columns =
    pass


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

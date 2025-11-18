# app.support.item.service.py
from sqlalchemy.ext.asyncio import AsyncSession

# from app.support.item.schemas import ItemCreate, ItemCreateRelation, ItemRead
from app.core.services.service import Service
from app.core.utils.alchemy_utils import JsonConverter
from app.core.utils.common_utils import get_value, jprint  # noqa: F401
from app.core.utils.io_utils import get_filepath_from_dir_by_name
from app.core.utils.json_validator import validate_json_file
from app.mongodb.service import ImageService
from app.support.drink.model import Drink
from app.support.drink.repository import DrinkRepository
from app.support.drink.service import DrinkService
from app.support.item.model import Item
from app.support.item.repository import ItemRepository
from app.support.item.schemas import ItemCreate, ItemCreateRelation, ItemRead


class ItemService(Service):
    default = ['vol', 'drink_id']

    @classmethod
    async def create_relation(cls, data: ItemCreateRelation,
                              repository: ItemRepository, model: Item,
                              session: AsyncSession) -> ItemRead:
        try:
            item_data: dict = data.model_dump(exclude={'drink', 'warehouse'},
                                              exclude_unset=True)
            if data.drink:
                try:
                    result = await DrinkService.create_relation(data.drink, DrinkRepository, Drink, session)
                    await session.commit()
                    # ошибка вот здесь.
                    item_data['drink_id'] = result.id
                except Exception as e:
                    print('data.drink.error::', result, e)
            # if data.warehouse:
            #     result = await WarehouseService.create_relation(data.warehouse, WarehouseRepository,
            #                                                     Warehouse, session)
            #     item_data['warehouse_id'] = result.id
            item = ItemCreate(**item_data)
            item_instance, _ = await cls.get_or_create(item, ItemRepository, Item, session)
            return item_instance
        except Exception as e:
            raise Exception(f'itemservice.create_relation. {e}')

    @classmethod
    async def direct_upload(cls, file_name: str, session: AsyncSession, image_service: ImageService) -> dict:
        try:
            # список ошибок
            error_list: list = []
            # путь к файлу для импорта
            filepath = get_filepath_from_dir_by_name(file_name)
            # получаем список кортежей (image_name, image_id)
            image_list = await image_service.get_images_list_after_date()
            # загружаем json файл, конвертируем в формат relation и собираем в список:
            dataconv: list = list(JsonConverter(filepath)().values())
            # проходим по списку и загружаем в postgresql
            expected_nmbr = validate_json_file(filepath)
            m = 0
            for n, item in enumerate(dataconv):
                try:
                    data_model = ItemCreateRelation(**item)
                    image_path = data_model.image_path
                    image_id = get_value(image_list, image_path) if image_list else None
                    data_model.image_id = image_id
                    result = await cls.create_relation(data_model, ItemRepository, Item, session)
                    if isinstance(result, Item):
                        m += 1
                    else:
                        error_list.append(item)
                except Exception as e:
                    print(f"{item.get('image_path', 'no image_path')}:: {e}")
                    # print(f'{item.get("image_path")}')
                    error_list.append(item)
                    # await session.rollback()
                    continue
            resu = {'total_input': expected_nmbr,
                    'count_of_added_records': n + 1 - len(error_list),
                    'error': error_list,
                    'error_nmbr': len(error_list)}  # {'filepath': len(dataconv)}
            return resu
        except Exception as e:
            print(f'Exception {e}')

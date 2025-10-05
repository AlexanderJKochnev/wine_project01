# app.support.item.service.py
# from pathlib import Path
from app.core.services.service import Service
# from app.core.config.project_config import settings
from app.core.utils.common_utils import jprint  # noqa: F401
from app.core.utils.alchemy_utils import JsonConverter
from app.core.utils.io_utils import get_filepath_from_dir_by_name
from app.support.item.router import Item, ItemCreate, ItemCreateRelations, ItemRepository, ItemRead, AsyncSession
from app.support.drink.router import DrinkService, DrinkRepository, Drink


class ItemService(Service):

    @classmethod
    async def create_relation(cls, data: ItemCreateRelations,
                              repository: ItemRepository, model: Item,
                              session: AsyncSession) -> ItemRead:
        try:
            item_data: dict = data.model_dump(exclude={'drink', 'warehouse'},
                                              exclude_unset=True)
            if data.drink:
                result = await DrinkService.create_relation(data.drink, DrinkRepository, Drink, session)
                item_data['drink_id'] = result.id
            # if data.warehouse:
            #     result = await WarehouseService.create_relation(data.warehouse, WarehouseRepository,
            #                                                     Warehouse, session)
            #     item_data['warehouse_id'] = result.id
            item = ItemCreate(**item_data)
            item_instance = await ItemService.get_or_create(item, ItemRepository, Item, session)
            return item_instance
        except Exception as e:
            raise Exception(f'ItemService.create_relation. {e}')

    @classmethod
    async def direct_upload(cls, session: AsyncSession) -> dict:
        try:
            # получаем путь к файлу json:
            error_list: list = []
            filepath = get_filepath_from_dir_by_name()
            # загружаем json файл, конвертируем в формат relation и собираем в список:
            dataconv: list = list(JsonConverter(filepath)().values())
            # проходим по списку и загружаем в postgresql
            for n, item in enumerate(dataconv):
                try:
                    data_model = ItemCreateRelations(**item)
                    await cls.create_relation(data_model, ItemRepository, Item, session)
                except Exception:
                    print(f'"{item.get('image_path', 'no image_path')}",')
                    error_list.append(item)
                    await session.rollback()
                    continue
            return {'error': error_list,
                    'error_nmbr': len(error_list)}  # {'filepath': len(dataconv)}
        except Exception as e:
            raise Exception(f'drink.service.direct_upload.error: {e}')

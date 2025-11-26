# app.support.item.service.py
from sqlalchemy.ext.asyncio import AsyncSession
from deepdiff import DeepDiff
from pydantic import ValidationError
# from app.support.item.schemas import ItemCreate, ItemCreateRelation, ItemRead
from app.core.services.service import Service
from app.core.utils.alchemy_utils import JsonConverter
from app.core.utils.common_utils import get_value, jprint  # noqa: F401
from app.core.utils.io_utils import get_filepath_from_dir_by_name
from app.core.utils.json_validator import validate_json_file
from app.mongodb.service import ThumbnailImageService
from app.support.drink.model import Drink
from app.support.drink.repository import DrinkRepository
from app.support.drink.service import DrinkService
from app.support.item.model import Item
from app.support.item.repository import ItemRepository
from app.support.item.schemas import ItemCreate, ItemCreateRelation, ItemRead, ItemReadRelation
from app.core.utils.converters import read_convert_json


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
            item_instance, new = await cls.get_or_create(item, ItemRepository, Item, session)
            return item_instance, new
        except Exception as e:
            raise Exception(f'itemservice.create_relation. {e}')

    @classmethod
    async def direct_upload(cls, file_name: dict, session: AsyncSession, image_service: ThumbnailImageService) -> dict:
        try:
            # получаем список кортежей (image_name, image_id)
            result: dict = {'total_input': 0,
                            'count_of_added_records': 0,
                            'error': [],
                            'error_nmbr': 0}
            # image_list = await image_service.get_images_list_after_date()
            for n, data in read_convert_json(file_name):
                result['total_input'] = result.get('total_input', 0) + 1
                instance = ItemCreateRelation.validate(data)
                # присваиваем значение image_id
                image_path = instance.image_path
                image_id = await image_service.get_id_by_filename(image_path)
                if not image_id:
                    raise Exception(f'{image_path=}======')
                instance.image_id = image_id
                data = instance.model_dump(exclude_unset=True, exclude_none=True)
                # old_dict = instance.model_dump(exclude_unset=True)
                # добавление instance базу данных
                try:
                    new_instance, new = await cls.create_relation(instance, ItemRepository, Item, session)
                    new_instance = await cls.get_by_id(new_instance.id, ItemRepository, Item, session)
                    new1 = ItemReadRelation.validate(new_instance)
                    new2 = new1.model_dump(exclude_unset=True, exclude_none=True)
                    diff = DeepDiff(new2, data,
                                    exclude_paths=["root['price']", "root['id']",
                                                   "root['drink']['id']",
                                                   "root['drink']['foods']",
                                                   "root['drink']['varietals']"]
                                    )
                    if diff:
                        print('исходные данные')
                        jprint(data)
                        print('сохраненный результат')
                        jprint(new2)
                        raise Exception(f'Ошибка сохранения записи uid {data.get("image_path")}'
                                        f'{diff}')
                    result['count_of_added_records'] = result.get('count_of_added_records', 0) + int(new)
                except ValidationError as exc:
                    jprint(data)
                    for error in exc.errors():
                        print(f"  Место ошибки (loc): {error['loc']}")
                        print(f"  Сообщение (msg): {error['msg']}")
                        print(f"  Тип ошибки (type): {error['type']}")
                        # input_value обычно присутствует в словаре ошибки
                        if 'input_value' in error:
                            print(f"  Некорректное значение (input_value): {error['input_value']}")
                        print("-" * 20)
                    assert False, 'ошибка валидации в методе ItemService.direct_upload'
                except Exception as e:
                    print(f'error: {e}')
                    result['error'] = result.get('error', []).append(instance.image_path)
                    result['error_nmbr'] = len(result.get('error', 0))
            return result
        except Exception as exc:
            print(f'{exc=}')

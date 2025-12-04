# app.support.item.service.py
from sqlalchemy.ext.asyncio import AsyncSession
from deepdiff import DeepDiff
from pydantic import ValidationError
# from app.support.item.schemas import ItemCreate, ItemCreateRelation, ItemRead
from app.core.services.service import Service
from app.core.utils.alchemy_utils import JsonConverter
from app.core.utils.common_utils import get_value, jprint, flatten_dict_with_localized_fields  # noqa: F401
from app.core.utils.io_utils import get_filepath_from_dir_by_name
from app.core.utils.json_validator import validate_json_file
from app.mongodb.service import ThumbnailImageService
from app.support.drink.model import Drink
from app.support.drink.repository import DrinkRepository
from app.support.drink.service import DrinkService
from app.support.item.model import Item
from app.support.item.repository import ItemRepository
from app.support.item.schemas import ItemCreate, ItemCreateRelation, ItemRead, ItemReadRelation, ItemListView, ItemDetailView
from app.core.utils.converters import read_convert_json


class ItemService(Service):
    default = ['vol', 'drink_id']

    @classmethod
    def _process_item_localization(cls, item, lang: str, fields_to_localize: list = None):
        """Внутренний метод для обработки локализации одного элемента"""
        if fields_to_localize is None:
            fields_to_localize = ['title', 'country', 'subcategory']
        
        # Подготовим данные для локализации
        localized_data = {
            'id': item['id'],
            'vol': item['vol'],
            'image_id': item['image_id'],
            'title': item['drink'].title,
            'title_ru': getattr(item['drink'], 'title_ru', ''),
            'title_fr': getattr(item['drink'], 'title_fr', ''),
            'country': item['country'].name if item['country'] else '',
            'country_ru': getattr(item['country'], 'name_ru', '') if item['country'] else '',
            'country_fr': getattr(item['country'], 'name_fr', '') if item['country'] else '',
            'subcategory': f"{item['subcategory'].category.name} {getattr(item['subcategory'], 'name', '')}",
            'subcategory_ru': f"{getattr(item['subcategory'].category, 'name_ru', '')} {getattr(item['subcategory'], 'name_ru', '')}" if (getattr(item['subcategory'].category, 'name_ru', None) and getattr(item['subcategory'], 'name_ru', None)) else '',
            'subcategory_fr': f"{getattr(item['subcategory'].category, 'name_fr', '')} {getattr(item['subcategory'], 'name_fr', '')}" if (getattr(item['subcategory'].category, 'name_fr', None) and getattr(item['subcategory'], 'name_fr', None)) else '',
        }
        
        # Применим функцию локализации
        localized_result = flatten_dict_with_localized_fields(
            localized_data, 
            fields_to_localize, 
            lang
        )
        
        # Добавим остальные поля
        localized_result['id'] = item['id']
        localized_result['vol'] = item['vol']
        localized_result['image_id'] = item['image_id']
        
        return localized_result

    @classmethod
    async def get_list_view(cls, lang: str, repository: ItemRepository, model: Item, session: AsyncSession):
        """Получение списка элементов для ListView с локализацией"""
        items = await repository.get_list_view(model, session)
        result = []
        for item in items:
            localized_result = cls._process_item_localization(item, lang)
            result.append(localized_result)
        return result

    @classmethod
    async def get_list_view_page(cls, page: int, page_size: int, repository: ItemRepository, model: Item, session: AsyncSession, lang: str = 'en'):
        """Получение списка элементов для ListView с пагинацией и локализацией"""
        skip = (page - 1) * page_size
        items, total = await repository.get_list_view_page(skip, page_size, model, session)
        result = []
        for item in items:
            localized_result = cls._process_item_localization(item, lang)
            result.append(localized_result)
        
        return {
            "items": result,
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_next": skip + len(items) < total,
            "has_prev": page > 1
        }

    @classmethod
    async def get_detail_view(cls, lang: str, id: int, repository: ItemRepository, model: Item, session: AsyncSession):
        """Получение детального представления элемента с локализацией"""
        item = await repository.get_detail_view(id, model, session)
        if not item:
            return None
            
        # Подготовим данные для локализации
        localized_data = {
            'id': item['id'],
            'vol': item['vol'],
            'alc': str(item['alc']) if item['alc'] is not None else None,
            'age': item['age'],
            'image_id': item['image_id'],
            'title': item['drink'].title,
            'title_ru': getattr(item['drink'], 'title_ru', ''),
            'title_fr': getattr(item['drink'], 'title_fr', ''),
            'subtitle': getattr(item['drink'], 'subtitle', ''),
            'subtitle_ru': getattr(item['drink'], 'subtitle_ru', ''),
            'subtitle_fr': getattr(item['drink'], 'subtitle_fr', ''),
            'country': item['country'].name if item['country'] else '',
            'country_ru': getattr(item['country'], 'name_ru', '') if item['country'] else '',
            'country_fr': getattr(item['country'], 'name_fr', '') if item['country'] else '',
            'subcategory': f"{item['subcategory'].category.name} {item['subcategory'].name}",
            'subcategory_ru': f"{getattr(item['subcategory'].category, 'name_ru', '')} {getattr(item['subcategory'], 'name_ru', '')}" if (getattr(item['subcategory'].category, 'name_ru', None) and getattr(item['subcategory'], 'name_ru', None)) else '',
            'subcategory_fr': f"{getattr(item['subcategory'].category, 'name_fr', '')} {getattr(item['subcategory'], 'name_fr', '')}" if (getattr(item['subcategory'].category, 'name_fr', None) and getattr(item['subcategory'], 'name_fr', None)) else '',
            'sweetness': getattr(item['sweetness'], 'name', '') if item['sweetness'] else '',
            'sweetness_ru': getattr(item['sweetness'], 'name_ru', '') if item['sweetness'] else '',
            'sweetness_fr': getattr(item['sweetness'], 'name_fr', '') if item['sweetness'] else '',
            'recommendation': getattr(item['drink'], 'recommendation', ''),
            'recommendation_ru': getattr(item['drink'], 'recommendation_ru', ''),
            'recommendation_fr': getattr(item['drink'], 'recommendation_fr', ''),
            'madeof': getattr(item['drink'], 'madeof', ''),
            'madeof_ru': getattr(item['drink'], 'madeof_ru', ''),
            'madeof_fr': getattr(item['drink'], 'madeof_fr', ''),
        }
        
        # Применим функцию локализации
        localized_result = flatten_dict_with_localized_fields(
            localized_data, 
            ['title', 'subtitle', 'country', 'subcategory', 'sweetness', 'recommendation', 'madeof'], 
            lang
        )
        
        # Добавим остальные поля
        localized_result['id'] = item['id']
        localized_result['vol'] = item['vol']
        localized_result['alc'] = str(item['alc']) if item['alc'] is not None else None
        localized_result['age'] = item['age']
        localized_result['image_id'] = item['image_id']
        
        return localized_result

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

# app/support/Item/repository.py

from sqlalchemy.orm import selectinload
from typing import Optional, List, Type, Tuple, Union
from sqlalchemy import func, select, Select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.repositories.sqlalchemy_repository import Repository
from app.support.drink.model import Drink, DrinkFood, DrinkVarietal
from app.support.drink.repository import DrinkRepository
from app.support.item.model import Item
from app.support.country.model import Country
from app.support.region.model import Region
from app.support.subregion.model import Subregion
from app.support.subcategory.model import Subcategory
from app.support.category.model import Category
from app.core.utils.alchemy_utils import ModelType, create_enum_conditions, create_search_conditions2
from app.core.services.logger import logger

# from app.core.config.database.db_noclass import get_db


# ItemRepository = RepositoryFactory.get_repository(Item)
class ItemRepository(Repository):
    model = Item

    @classmethod
    def get_query2(csl, model: ModelType):
        """ Добавляем загрузку связи с relationships
            Обратить внимание! для последовательной загрузки использовать точку.
            параллельно запятая
        """
        return select(Item).options(selectinload(Item.drink).
                                    selectinload(Drink.subregion).
                                    selectinload(Subregion.region).
                                    selectinload(Region.country),
                                    selectinload(Item.drink).
                                    selectinload(Drink.subcategory).
                                    selectinload(Subcategory.category),
                                    selectinload(Drink.sweetness),
                                    selectinload(Item.drink).
                                    selectinload(Drink.foods),
                                    selectinload(Drink.food_associations).joinedload(DrinkFood.food),
                                    selectinload(Drink.varietals),
                                    selectinload(Drink.varietal_associations).joinedload(DrinkVarietal.varietal))

    @classmethod
    def get_query(cls, model: ModelType):
        return select(model).options(
            selectinload(Item.drink).options(
                selectinload(Drink.subregion).options(
                    selectinload(Subregion.region).options(
                        selectinload(Region.country)
                    )
                ),
                selectinload(Drink.subcategory).selectinload(Subcategory.category),
                selectinload(Drink.sweetness), selectinload(Drink.foods),
                selectinload(Drink.food_associations).joinedload(DrinkFood.food), selectinload(Drink.varietals),
                selectinload(Drink.varietal_associations).joinedload(DrinkVarietal.varietal)
            ),
        )

    @classmethod
    async def search_in_main_table(cls,
                                   search_str: str,
                                   model: Type[Item],
                                   session: AsyncSession,
                                   skip: int = None,
                                   limit: int = None,
                                   category_enum: str = None,
                                   country_enum: str = None) -> Optional[List[ModelType]]:
        """Поиск по всем заданным текстовым полям основной таблицы
            НЕ ИСПОЛЬЗУЕТСЯ УДАЛИТЬ
        """
        try:
            # ищем в Drink (диапазон расширяем в два раза что бы охватить все Items
            # ищем category_id:
            dlimit = limit * 2 if limit else limit
            if skip and limit:
                dskip = skip if skip == 0 else skip - limit
            else:
                dskip = None
            drinks, count = await DrinkRepository.search_in_main_table(search_str, Drink, session,
                                                                       skip=dskip, limit=dlimit,
                                                                       category_enum=category_enum,
                                                                       country_enum=country_enum)
            if count == 0:
                records = []
                total = 0
            else:
                conditions = [a.id for a in drinks]
                query = cls.get_query(model).where(model.drink_id.in_(conditions))
                # получаем общее количество записей удовлетворяющих условию
                count = select(func.count()).select_from(model).where(model.drink_id.in_(conditions))
                result = await session.execute(count)
                total = result.scalar()
                # Добавляем пагинацию если указано
                if limit is not None:
                    query = query.limit(limit)
                if skip is not None:
                    query = query.offset(skip)
                result = await session.execute(query)
                records = result.scalars().all()
            return (records if records else [], total)
        except Exception as e:
            logger.error(f'ошибка search_in_main_table: {e}')
            print(f'search_in_main_table.error: {e}')

    @classmethod
    def apply_search_filter(cls, model: Union[Select[Tuple], ModelType], **kwargs):
        """
            переопределяемый метод, стоит условия поиска и пагинации при необходимости
            категория wine имеет подкатегории которые как-бы категории поэтому костыль
        """
        wine = ['red', 'white', 'rose', 'sparkling', 'port']
        if not isinstance(model, Select):   # подсчет количества
            query = cls.get_query(Item).join(Item.drink)
        else:
            query = model.join(Item.drink)
        search_str: str = kwargs.get('search_str')
        category_enum: str = kwargs.get('category_enum')
        country_enum: str = kwargs.get('country_enum')
        if category_enum:
            if category_enum in wine:
                subcategory_cond = create_enum_conditions(Subcategory, category_enum)
                query = (query.join(Drink.subcategory).where(subcategory_cond))
            else:
                category_cond = create_enum_conditions(Category, category_enum)
                query = (query
                         .join(Drink.subcategory)
                         .join(Subcategory.category).where(category_cond))
        if country_enum:
            country_cond = create_enum_conditions(Country, country_enum)
            query = (query.join(Drink.subregion)
                     .join(Subregion.region)
                     .join(Region.country).where(country_cond))
        if search_str:
            search_cond = create_search_conditions2(Drink, search_str)
            query = query.where(search_cond)
        return query

    @classmethod
    async def get_list_view(cls, model: ModelType, session: AsyncSession):
        """Получение списка элементов с плоскими полями для ListView"""
        query = select(Item).options(
            selectinload(Item.drink).options(
                selectinload(Drink.subregion).options(
                    selectinload(Subregion.region).options(
                        selectinload(Region.country)
                    )
                ),
                selectinload(Drink.subcategory).selectinload(Subcategory.category),
                selectinload(Drink.sweetness)
            )
        )
        
        result = await session.execute(query)
        items = result.scalars().all()
        
        # Преобразуем в плоские словари
        flat_items = []
        for item in items:
            flat_item = {
                'id': item.id,
                'vol': item.vol,
                'image_id': item.image_id,
                'title': item.drink.title,  # будет обработано в сервисе для нужного языка
                'drink': item.drink,
                'subcategory': item.drink.subcategory,
                'country': item.drink.subregion.region.country
            }
            flat_items.append(flat_item)
        
        return flat_items

    @classmethod
    async def get_detail_view(cls, id: int, model: ModelType, session: AsyncSession):
        """Получение детального представления элемента для DetailView"""
        query = select(Item).options(
            selectinload(Item.drink).options(
                selectinload(Drink.subregion).options(
                    selectinload(Subregion.region).options(
                        selectinload(Region.country)
                    )
                ),
                selectinload(Drink.subcategory).selectinload(Subcategory.category),
                selectinload(Drink.sweetness),
                selectinload(Drink.food_associations).joinedload(DrinkFood.food),
                selectinload(Drink.varietal_associations).joinedload(DrinkVarietal.varietal)
            )
        ).where(Item.id == id)
        
        result = await session.execute(query)
        item = result.scalar_one_or_none()
        
        if not item:
            return None
            
        # Преобразуем в плоский словарь для детального представления
        flat_item = {
            'id': item.id,
            'vol': item.vol,
            'alc': item.drink.alc,
            'age': item.drink.age,
            'image_id': item.image_id,
            'title': item.drink.title,  # будет обработано в сервисе для нужного языка
            'drink': item.drink,
            'country': item.drink.subregion.region.country,
            'subcategory': item.drink.subcategory,
            'sweetness': item.drink.sweetness
        }
        
        return flat_item

    @classmethod
    async def get_list_view_page(cls, skip: int, limit: int, model: ModelType, session: AsyncSession):
        """Получение списка элементов с плоскими полями для ListView с пагинацией"""
        query = select(Item).options(
            selectinload(Item.drink).options(
                selectinload(Drink.subregion).options(
                    selectinload(Subregion.region).options(
                        selectinload(Region.country)
                    )
                ),
                selectinload(Drink.subcategory).selectinload(Subcategory.category),
                selectinload(Drink.sweetness)
            )
        )
        
        count_query = select(func.count()).select_from(Item)
        count_result = await session.execute(count_query)
        total = count_result.scalar()
        
        query = query.offset(skip).limit(limit)
        result = await session.execute(query)
        items = result.scalars().all()
        
        # Преобразуем в плоские словари
        flat_items = []
        for item in items:
            flat_item = {
                'id': item.id,
                'vol': item.vol,
                'image_id': item.image_id,
                'title': item.drink.title,  # будет обработано в сервисе для нужного языка
                'drink': item.drink,
                'subcategory': item.drink.subcategory,
                'country': item.drink.subregion.region.country
            }
            flat_items.append(flat_item)
        
        return flat_items, total

# app/support/Item/repository.py

from sqlalchemy.orm import selectinload
from typing import Optional, List, Type
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.repositories.sqlalchemy_repository import Repository
from app.support.drink.model import Drink, DrinkFood, DrinkVarietal
from app.support.drink.router import DrinkRepository
from app.support.item.model import Item
from app.support.region.model import Region
from app.support.subregion.model import Subregion
from app.support.subcategory.model import Subcategory
from app.core.utils.alchemy_utils import ModelType
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
            # selectinload(Item.warehouse)
        )

    @classmethod
    async def search_in_main_table(cls,
                                   search_str: str,
                                   model: Type[Item],
                                   session: AsyncSession,
                                   skip: int = None,
                                   limit: int = None) -> Optional[List[ModelType]]:
        """Поиск по всем заданным текстовым полям основной таблицы"""
        try:
            # ищем в Drink
            drinks, count = await DrinkRepository.search_in_main_table(search_str, Drink, session)
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

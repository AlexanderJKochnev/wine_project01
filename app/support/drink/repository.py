# app/support/drink/repository.py
from typing import Type, Optional, List
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.services.logger import logger
from app.core.repositories.sqlalchemy_repository import Repository, ModelType
from app.support.drink.model import Drink, DrinkFood, DrinkVarietal
from app.support.subregion.model import Subregion
from app.support.region.model import Region
from app.support.subcategory.model import Subcategory


class DrinkRepository(Repository):
    model = Drink

    @classmethod
    def get_query(csl, model: ModelType):
        """ Добавляем загрузку связи с relationships
            Обратить внимание! для последовательной загрузки использовать точку.
            параллельно запятая
        """
        return select(Drink).options(selectinload(Drink.subregion).
                                     selectinload(Subregion.region).
                                     selectinload(Region.country),
                                     selectinload(Drink.subcategory).
                                     selectinload(Subcategory.category),
                                     selectinload(Drink.sweetness),
                                     selectinload(Drink.foods),
                                     selectinload(Drink.food_associations).joinedload(DrinkFood.food),
                                     selectinload(Drink.varietals),
                                     selectinload(Drink.varietal_associations).joinedload(DrinkVarietal.varietal))

    @classmethod
    async def search_in_main_table(cls,
                                   search_str: str,
                                   model: Type[Drink],
                                   session: AsyncSession,
                                   skip: int = None,
                                   limit: int = None,
                                   category_enum: str = None,
                                   country_enum: str = None) -> Optional[List[ModelType]]:
        """Поиск по всем заданным текстовым полям основной таблицы"""
        try:
            if category_enum:   # ищем в subcategory->category
                Drink.subcategory
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

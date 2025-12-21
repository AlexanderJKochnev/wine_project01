# app/support/drink/drink_varietal_repo.py
from typing import Dict

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.support.drink.model import Drink, DrinkVarietal
from app.support.varietal.model import Varietal


class DrinkVarietalRepository:

    @classmethod
    async def get_drink_with_varietals(cls, drink_id: int, session: AsyncSession):
        result = await session.execute(
            select(Drink)
            .where(Drink.id == drink_id)
            .options(selectinload(Drink.varietal_associations).joinedload(DrinkVarietal.varietal))
        )
        return result.scalar_one_or_none()

    @classmethod
    async def get_varietal_with_drinks(cls, varietal_id: int, session: AsyncSession):
        result = await session.execute(
            select(Varietal)
            .where(Varietal.id == varietal_id)
            .options(selectinload(Varietal.drink_associations).joinedload(DrinkVarietal.drink))
        )
        return result.scalar_one_or_none()

    @classmethod
    async def add_varietal_to_drink(cls, drink_id: int, varietal_id: int, percentage: int, session: AsyncSession):
        """
            добавление одной записи
        """
        try:
            association = DrinkVarietal(drink_id=drink_id, varietal_id=varietal_id, percentage=percentage)
            session.add(association)
            await session.commit()
            return association
        except Exception as e:
            raise Exception(f"ошибка выполнения метода DrinkVarietalRepository.add_varietal_to_drink."
                            f"{drink_id=}, {varietal_id=}, {percentage=}. {e}")

    @classmethod
    async def remove_varietal_from_drink(cls, drink_id: int, varietal_id: int, session: AsyncSession):
        """
            удалеени однйо записи
        """
        stmt = select(DrinkVarietal).where(DrinkVarietal.drink_id == drink_id, DrinkVarietal.varietal_id == varietal_id)
        result = await session.execute(stmt)
        association = result.scalar_one_or_none()
        if association:
            await session.delete(association)
            await session.commit()

    @classmethod
    async def update_percentage(cls, drink_id: int, varietal_id: int, percentage: int, session: AsyncSession):
        """
            обновление процентов
        """
        stmt = select(DrinkVarietal).where(DrinkVarietal.drink_id == drink_id, DrinkVarietal.varietal_id == varietal_id)
        result = await session.execute(stmt)
        association = result.scalar_one_or_none()
        if association:
            association.percentage = percentage
            await session.commit()

    @classmethod
    async def set_drink_varietals(cls, drink_id: int, varietal_ids: list[int], session: AsyncSession):
        """Полная замена связей (для update)"""
        # Удаляем старые
        # stmt = select(DrinkVarietal).where(DrinkVarietal.drink_id == drink_id).execution_options(yield_per=1000)
        # result = session.scalars(stmt).yield_per(100)
        # for obj in result:
        #     await session.delete(obj)
        # await session.commit()
        # альтернативный способ удаления записей - быстрее но не поддердивает ORM-логику
        await session.execute(delete(DrinkVarietal).where(DrinkVarietal.drink_id == drink_id))
        # Добавляем новые
        associations = [
            DrinkVarietal(drink_id=drink_id, varietal_id=varietal_id, percentage=0)
            for varietal_id in varietal_ids
        ]
        session.add_all(associations)
        await session.commit()

    @classmethod
    async def set_drink_varietals_with_percentage(cls, drink_id: int,
                                                  varietal_dict: Dict[int, float], session: AsyncSession):
        """Полная замена связей (для update)"""
        # Удаляем старые
        # stmt = select(DrinkVarietal).where(DrinkVarietal.drink_id == drink_id).execution_options(yield_per=1000)
        # result = session.scalars(stmt).yield_per(100)
        # for obj in result:
        #     await session.delete(obj)
        # await session.commit()
        # альтернативный способ удаления записей - быстрее но не поддердивает ORM-логику
        try:
            await session.execute(delete(DrinkVarietal).where(DrinkVarietal.drink_id == drink_id))
            # Добавляем новые
            associations = [DrinkVarietal(drink_id=drink_id, varietal_id=key, percentage=val)
                            for key, val in varietal_dict.items()]
            session.add_all(associations)
            await session.commit()
            return True
        except Exception as e:
            print(f'set_drink_varietals_with_percentage.error {e}')

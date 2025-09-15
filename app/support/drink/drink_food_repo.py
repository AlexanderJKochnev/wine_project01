# app/support/drink/drink_food_repo.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.support.drink.model import Drink, DrinkFood
from app.support.food.model import Food


class DrinkFoodRepository:

    @classmethod
    async def get_drink_with_foods(cls, drink_id: int, session: AsyncSession):
        result = await session.execute(
            select(Drink)
            .where(Drink.id == drink_id)
            .options(selectinload(Drink.food_associations).joinedload(DrinkFood.food))
        )
        return result.scalar_one_or_none()

    async def get_food_with_drinks(cls, food_id: int, ):
        result = await self.session.execute(
            select(Food)
            .where(Food.id == food_id)
            .options(selectinload(Food.drink_associations).joinedload(DrinkFood.drink))
        )
        return result.scalar_one_or_none()

    async def add_food_to_drink(self, drink_id: int, food_id: int, priority: int, session: AsyncSession):
        association = DrinkFood(drink_id=drink_id, food_id=food_id, priority=priority)
        session.add(association)
        await self.session.commit()
        # await self.session.refresh()
        # return association

    async def remove_food_from_drink(self, drink_id: int, food_id: int, session: AsyncSession):
        stmt = select(DrinkFood).where(DrinkFood.drink_id == drink_id, DrinkFood.food_id == food_id)
        result = await session.execute(stmt)
        association = result.scalar_one_or_none()
        if association:
            await self.session.delete(association)
            await self.session.commit()

    async def update_priority(self, drink_id: int, food_id: int, priority: int, session: AsyncSession):
        stmt = select(DrinkFood).where(DrinkFood.drink_id == drink_id, DrinkFood.food_id == food_id)
        result = await session.execute(stmt)
        association = result.scalar_one_or_none()
        if association:
            association.priority = priority
            await self.session.commit()

    async def set_drink_foods(self, drink_id: int, food_ids: list[int], session: AsyncSession):
        """Полная замена связей (для update)"""
        # Удаляем старые
        stmt = select(DrinkFood).where(DrinkFood.drink_id == drink_id).execution_options(yield_per=1000)
        result = session.scalars(stmt).yield_per(100)
        for obj in result:
            await session.delete(obj)
        await session.commit()
        # альтернативный способ удаления записей - быстрее но не поддердивает ORM-логику
        # await self.session.execute(delete(DrinkFood).where(DrinkFood.drink_id == drink_id))
        # Добавляем новые
        associations = [
            DrinkFood(drink_id=drink_id, food_id=food_id, priority=0)
            for food_id in food_ids
        ]
        self.session.add_all(associations)
        await self.session.commit()

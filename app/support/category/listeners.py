# app/support/category/listeners.py
#  удалить
from sqlalchemy import update, event, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from app.support.drink.model import Drink
from app.support.category.model import Category
from app.core.config.database.db_async import get_db


async def increment_drink_count(category_id: int, session: AsyncSession):
    await session.execute(
        update(Category)
        .where(Category.id == category_id)
        .values(count_drink=Category.count_drink + 1)
    )


async def decrement_drink_count(category_id: int, session: AsyncSession):
    await session.execute(
        update(Category)
        .where(Category.id == category_id)
        .values(count_drink=Category.count_drink - 1)
    )


# === Обработчики событий ===

@event.listens_for(Drink, "after_insert")
async def after_drink_insert(mapper, connection, target):
    async with get_db() as session:
        await increment_drink_count(target.category_id, session)
        await session.commit()


@event.listens_for(Drink, "before_update")
async def before_drink_update(mapper, connection, target):
    # Получаем старое значение category_id
    session = Session.object_session(target)
    if session:
        # Загружаем старое состояние
        stmt = select(Drink).with_only_columns(Drink.category_id).where(Drink.id == target.id).with_session(session)
        result = await session.execute(stmt)
        old_category_id = result.scalar()

        if old_category_id and old_category_id != target.category_id:
            # Категория изменилась
            await decrement_drink_count(old_category_id, session)
            await increment_drink_count(target.category_id, session)
            await session.commit()


@event.listens_for(Drink, "before_delete")
async def before_drink_delete(mapper, connection, target):
    async with get_db() as session:
        await decrement_drink_count(target.category_id, session)
        await session.commit()

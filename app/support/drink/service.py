""" Data Access Object  """
from sqlalchemy import event, insert, select
from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from app.core.config.database.db_noclass import async_session_maker
from app.core.services.base import BaseDAO
from app.support.category.models import Category
from app.support.drink.models import Drink


class DrinkDAO(BaseDAO):
    model = Drink

    @classmethod
    async def find_full_data(cls, drink_id: int):
        async with async_session_maker() as session:
            # Первый запрос для получения информации о напитке
            query = select(cls.model).options(
                joinedload(cls.model.category)).filter_by(id=drink_id)
            # query_student = select(cls.model).filter_by(id=student_id)
            result = await session.execute(query)
            drink_info = result.scalar_one_or_none()

            # Если запись не найдена, возвращаем None
            if not drink_info:
                return None

            drink_data = drink_info.to_dict()
            drink_data['category'] = drink_info.category.category_name
            return drink_data

            # Второй запрос для получения информации о категории
            # query_category = select(Category).filter_by(
            #      id=drink_info.category_id)
            # result_category = await session.execute(query_category)
            # category_info = result_category.scalar_one()

            # drink_data = drink_info.to_dict()
            # drink_data['category'] = category_info.category_name

            # return drink_data

    @classmethod
    async def add_drink_long(cls, drink_data: dict):
        async with async_session_maker() as session:
            async with session.begin():
                # Вставка нового drink
                stmt = insert(cls.model).values(**drink_data).returning(
                    cls.model.id, cls.model.drink_id)
                result = await session.execute(stmt)
                new_drink_id, category_id = result.fetchone()

                # Увеличение счетчика drink в таблице Category ?
                update_category = (
                    update(Category)
                    .where(Category.id == category_id)
                    .values(count_drink=Category.count_drink + 1)
                )
                await session.execute(update_category)

                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e

                return new_drink_id

    @event.listens_for(Drink, 'after_insert')
    def receive_after_insert(mapper, connection, target):
        """ событие after insert записи в Drink"""
        category_id = target.category_id
        connection.execute(
            update(Category)
            .where(Category.id == category_id)
            .values(count_drink=Category.count_drink + 1)
        )

    @event.listens_for(Drink, 'after_delete')
    def receive_after_delete(mapper, connection, target):
        """событие after delete записи из Student"""
        category_id = target.category_id
        connection.execute(
            update(Category)
            .where(Category.id == category_id)
            .values(count_drink=Category.count_drink - 1)
        )

    @classmethod
    async def add_drink(cls, drink_data: dict):
        async with async_session_maker() as session:
            async with session.begin():
                new_drink = Drink(**drink_data)
                session.add(new_drink)
                await session.flush()
                new_drink_id = new_drink.id
                await session.commit()
                return new_drink_id

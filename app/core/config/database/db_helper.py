# app/core/config/database/db_helper.py
""" not used - see db_noclass"""
from asyncio import current_task
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession, AsyncEngine,
    create_async_engine,
    async_sessionmaker,
    async_scoped_session
)

from app.core.config.database.db_config import settings_db
from fastapi import Depends


class DatabaseHelper:
    """ Session Factory for Postgresql
        при каждом вызове создает новую сессию
    """
    def __init__(self, url: str, echo: bool = True):
        self.engine: AsyncEngine = create_async_engine(
            url=url,    # строка подключения
            echo=echo,  # логирование SQL-запросов (выключить в продакшене)
            pool_pre_ping=True)
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False
        )

    def get_scope_session(self):
        """
        Гарантирует одну сессию на контекст (например, на запрос).
        когда это нужно - разобраться
        не забывать ее закрывать
        """
        return async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task
        )

    @asynccontextmanager
    async def get_db_session(self):
        """ @asynccontextmanager may not work properly. alternative see
        bellow """
        from sqlalchemy import exc

        session: AsyncSession = self.session_factory()
        try:
            yield session
        except exc.SQLAlchemyError:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def get_db(self):
        """Зависимость для внедрения сессии в маршруты."""
        async with self.session_factory() as session:
            yield session


db_help = DatabaseHelper(settings_db.database_url, settings_db.DB_ECHO_LOG)

# tests/_test_database1.py
from sqlalchemy import text
import pytest
from app.core.models.base_model import Base

pytestmark = pytest.mark.asyncio


async def test_connection(async_db_engine):
    """ тестирование двигателя """
    engine = async_db_engine
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT version()"))
        assert result.scalar().startswith('PostgreSQL')


async def test_connection1(async_db_engine):
    """ тестирование двигателя """
    engine = async_db_engine
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        assert 1 == 2, result.scalar()

# tests/test_database.py
import pytest
from sqlalchemy import text
from app.core.models.base_model import Base
from sqlalchemy import select
from app.auth.models import User
"""
from app.support.category.model import Category
from app.support.drink.model import Drink
from app.support.country.model import Country
from app.support.customer.model import Customer
from app.support.warehouse.model import Warehouse
from app.support.food.model import Food
from app.support.item.model import Item
from app.support.region.model import Region
from app.support.sweetness.model import Sweetness
from app.auth.models import User
"""

pytestmark = pytest.mark.asyncio


async def test_all_tables_created(mock_engine):
    """Тест проверяет, что все таблицы созданы в тестовой базе данных"""
    async with mock_engine.connect() as conn:
        # Получаем список всех таблиц
        if "sqlite" in str(mock_engine.url):
            # Для SQLite
            result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            tables = [row[0] for row in result.fetchall()]
        else:
            # Для PostgreSQL/MySQL
            result = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public';"))
            tables = [row[0] for row in result.fetchall()]
        # Проверяем наличие всех ожидаемых таблиц
        expected_tables = {'categories', 'drinks', 'countries', 'customers',
                           'warehouses', 'foods', 'items', 'regions',
                           'sweetness', 'users'}

        # Для SQLite таблицы могут иметь немного другие имена
        found_tables = set(tables)
        missing_tables = expected_tables - found_tables

        # Проверяем, что все основные таблицы существуют
        assert len(missing_tables) == 0, f"Missing tables: {missing_tables}"

        # Проверяем, что таблицы имеют правильную структуру
        for table_name in expected_tables:
            if table_name in found_tables:
                # Проверяем, что таблица не пустая (имеет столбцы)
                try:
                    if "sqlite" in str(mock_engine.url):
                        result = await conn.execute(text(f"PRAGMA table_info('{table_name}');"))
                    else:
                        result = await conn.execute(
                            text(
                                f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';"
                            )
                        )
                    columns = result.fetchall()
                    assert len(columns) > 0, f"Table {table_name} has no columns"
                except Exception as e:
                    # Некоторые таблицы могут не существовать в тестовой среде
                    assert False, f"Warning: Could not check table {table_name}: {e}"


async def test_database_metadata_consistency(mock_engine):
    """Тест проверяет, что метаданные SQLAlchemy соответствуют созданным таблицам"""
    # Получаем все таблицы из метаданных
    metadata_tables = set(Base.metadata.tables.keys())

    # Получаем все созданные таблицы
    async with mock_engine.connect() as conn:
        if "sqlite" in str(mock_engine.url):
            result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            created_tables = set([row[0] for row in result.fetchall()])
        else:
            result = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public';"))
            created_tables = set([row[0] for row in result.fetchall()])

    # Проверяем, что все таблицы из метаданных созданы
    # Исключаем служебные таблицы
    metadata_tables_clean = {table for table in metadata_tables if not table.startswith('alembic')}
    created_tables_clean = {table for table in created_tables if not table.startswith('alembic')}

    missing_in_db = metadata_tables_clean - created_tables_clean
    # extra_in_db = created_tables_clean - metadata_tables_clean

    assert len(
        missing_in_db
    ) == 0, f"Tables missing in database: {missing_in_db}"
    # Дополнительные таблицы в БД допустимы (например, служебные)


async def test_table_relationships_exist(mock_engine):
    """Тест проверяет, что таблицы с foreign key relationships существуют"""
    expected_relationships = [('drinks', 'categories'),  # drinks.category_id -> categories.id
                              ('drinks', 'regions'),  # drinks.region_id -> regions.id
                              ('regions', 'countries'),  # regions.country_id -> countries.id
                              ('items', 'drinks'),]  # items.drink_id -> drinks.id

    async with mock_engine.connect() as conn:
        if "sqlite" in str(mock_engine.url):
            # Для SQLite проверяем существование таблиц
            for child_table, parent_table in expected_relationships:
                try:
                    await conn.execute(text(f"SELECT * FROM {child_table} LIMIT 0;"))
                    await conn.execute(text(f"SELECT * FROM {parent_table} LIMIT 0;"))
                except Exception as e:
                    pytest.fail(f"Table relationship check failed for {child_table} -> {parent_table}: {e}")


async def test_superuser_exist(test_db_session, create_super_user, super_user_data):
    """  проверяет наличие пользователя с правами суперюзера"""
    username = super_user_data.get('username')
    stmt = select(User).where(User.username == username)
    result = await test_db_session.execute(stmt)
    admin_user = result.scalar_one_or_none()

    assert admin_user is not None, "Superuser 'admin' should exist in test database"
    assert admin_user.username == super_user_data.get("username")
    assert admin_user.email == super_user_data.get('email')
    assert admin_user.is_active is True
    assert admin_user.is_superuser is True
    assert admin_user.hashed_password is not None
    assert len(admin_user.hashed_password) > 0

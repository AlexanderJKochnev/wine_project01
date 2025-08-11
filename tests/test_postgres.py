# tests/test_postgres.py

import pytest
import asyncpg
from asyncpg import Connection

# Ваша строка подключения
DB_URL = "postgresql+asyncpg://wine:wine1@wine_host:5432/wine_db"

# Преобразуем URL в формат, понятный asyncpg (удаляем +asyncpg)
ASYNC_PG_URL = DB_URL.replace("postgresql+asyncpg://", "postgres://")


@pytest.mark.asyncio
async def test_db_connection():
    """Тест проверяет, что подключение к базе данных работает."""
    conn: Connection = None
    try:
        # Подключаемся к базе данных
        conn = await asyncpg.connect(ASYNC_PG_URL)

        # Выполняем простой запрос для проверки соединения
        result = await conn.fetchval("SELECT 1")
        assert result == 1, "Тестовый запрос должен вернуть 1"

    except Exception as e:
        # Если возникло исключение - тест провален
        pytest.fail(f"Ошибка подключения к базе данных: {str(e)}")
    finally:
        # Всегда закрываем соединение
        if conn:
            await conn.close()


@pytest.mark.asyncio
async def test_db_version():
    """Тест проверяет, что можем получить версию PostgreSQL."""
    conn: Connection = None
    try:
        conn = await asyncpg.connect(ASYNC_PG_URL)
        version = await conn.fetchval("SELECT version()")
        assert "PostgreSQL" in version, "Должна возвращаться версия PostgreSQL"
        print(f"\nВерсия PostgreSQL: {version}")
    finally:
        if conn:
            await conn.close()

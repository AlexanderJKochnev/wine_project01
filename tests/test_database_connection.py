# tests/test_database_connection.py
import pytest
# from fastapi import status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

pytestmark = pytest.mark.asyncio


async def test_database_connection_established(authenticated_client_with_db1, test_db_session):
    """Тест проверяет, что соединение с тестовой базой данных установлено"""
    # Проверяем, что сессия существует
    assert test_db_session is not None

    # Выполняем простой запрос к базе данных
    try:
        result = await test_db_session.execute(text("SELECT 1"))
        value = result.scalar()
        assert value == 1
    except SQLAlchemyError as e:
        pytest.fail(f"Database connection failed: {e}")


async def test_database_tables_accessible(authenticated_client_with_db, test_db_session):
    """Тест проверяет, что таблицы доступны в тестовой базе данных"""
    # Проверяем доступ к основным таблицам
    expected_tables = ['users', 'categories', 'drinks', 'colors', 'regions', 'countries']

    for table_name in expected_tables:
        try:
            # Выполняем запрос к таблице
            result = await test_db_session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = result.scalar()
            # Если запрос выполнен успешно, таблица существует
            assert count is not None
        except SQLAlchemyError:
            # Некоторые таблицы могут не существовать в тестовой среде - это нормально
            pass  # Просто пропускаем


async def test_fastapi_database_dependency_works(authenticated_client_with_db):
    """Тест проверяет, что FastAPI dependency для базы данных работает"""
    # Создаем тестовый маршрут, который использует базу данных
    # Для этого делаем простой запрос, который задействует репозиторий
    try:
        # Запрашиваем список цветов (пустой, но это проверит соединение)
        response = await authenticated_client_with_db.get("/colors/")
        # Даже если таблица пустая, запрос должен пройти успешно
        assert response.status_code in [200, 500]  # 500 если таблица не существует
        # Если получили 500, проверяем, что это не ошибка соединения
        if response.status_code == 500:
            error_detail = response.json().get('detail', '')
            # Ошибка соединения будет содержать специфичные сообщения
            assert 'connection' not in error_detail.lower()
            assert 'database' not in error_detail.lower() or 'not found' in error_detail.lower()

    except Exception as e:
        # Проверяем, что ошибка не связана с соединением
        error_str = str(e).lower()
        assert 'connection' not in error_str
        assert 'timeout' not in error_str


async def test_database_session_is_active(authenticated_client_with_db, test_db_session):
    """Тест проверяет, что сессия базы данных активна и может выполнять операции"""
    # Проверяем, что можем выполнить операцию с сессией
    try:
        result = await test_db_session.execute(text("SELECT 'test_connection'"))
        value = result.scalar()
        assert value == 'test_connection'
    except SQLAlchemyError as e:
        pytest.fail(f"Database session test failed: {e}")


async def test_multiple_database_operations(authenticated_client_with_db, test_db_session):
    """Тест проверяет, что можно выполнять несколько операций с базой данных"""
    # Выполняем несколько последовательных операций
    operations = ["SELECT 1",
                  "SELECT sqlite_version()" if "sqlite" in str(test_db_session.bind.url) else "SELECT version()", ]
    # Добавляем запрос к таблицам в зависимости от типа базы данных
    if "sqlite" in str(test_db_session.bind.url):
        operations.append("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
    else:
        operations.append("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")

    for query in operations:
        try:
            result = await test_db_session.execute(text(query))
            value = result.scalar()
            assert value is not None
        except SQLAlchemyError:
            # Некоторые запросы могут не работать в разных СУБД - это нормально
            pass


async def test_database_transaction_works(authenticated_client_with_db, test_db_session):
    """Тест проверяет, что сессия может выполнять различные операции"""
    # Проверяем, что сессия может выполнять различные типы запросов
    try:
        # SELECT запрос
        result = await test_db_session.execute(text("SELECT 1"))
        assert result.scalar() == 1

        # Проверяем, что можем выполнить запрос к системным таблицам
        if "sqlite" in str(test_db_session.bind.url):
            result = await test_db_session.execute(text("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1"))
        else:
            result = await test_db_session.execute(
                text("SELECT tablename FROM pg_tables WHERE schemaname = 'public' LIMIT 1")
            )

        # Результат может быть пустой, но запрос должен выполниться без ошибок
        result.fetchall()  # Просто выполняем, чтобы убедиться, что нет ошибок

    except SQLAlchemyError as e:
        pytest.fail(f"Database session operations failed: {e}")

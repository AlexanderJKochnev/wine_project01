from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import asyncio
from sqlalchemy import text
from app.core.config.database.db_config import settings_db
from app.core.models.base_model import Base


# URL для асинхронного подключения
# ASYNC_DATABASE_URL = "postgresql+asyncpg://wine:wine1@localhost:5432/wine_db"
ASYNC_DATABASE_URL = "postgresql+asyncpg://test_user:test@localhost:2345/test_db"
print(f'{settings_db.database_url=}')
# Создание асинхронного engine
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def create_tables():
    """Создание всех таблиц в базе данных"""
    async with async_engine.begin() as conn:
        # Вот правильное использование run_sync
        await conn.run_sync(Base.metadata.create_all)
        print("Таблицы успешно созданы!")


async def test_connection():
    """Тест подключения и проверка таблиц"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            )
        tables = result.scalars().all()
        print(f"Найдены таблицы: {tables}")


async def main():
    try:
        # Создаем таблицы
        await create_tables()
        
        # Проверяем, что таблицы создались
        await test_connection()
        
        print("Все операции завершены успешно!")
    
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        # Закрываем engine
        await async_engine.dispose()


# Запуск
if __name__ == "__main__":
    asyncio.run(main())

# -------------------
"""
async def test_connection():
    async with async_engine.connect() as conn:
        result = await conn.execute(text("SELECT version()"))
        print("PostgreSQL version:", result.scalar())
        print("Асинхронное подключение успешно!")
        await conn.run_sync(Base.metadata.create_all)

#     async with async_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

# Запуск проверки
asyncio.run(test_connection())
"""

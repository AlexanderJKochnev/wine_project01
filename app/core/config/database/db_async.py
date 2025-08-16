# app/core/config/database/db_async.py
# асинхронный драйвер
from sqlalchemy.ext.asyncio import (create_async_engine,
                                    async_sessionmaker,
                                    AsyncEngine,
                                    AsyncSession)
from app.core.config.database.db_config import settings_db

# 1.    Асинхронный двигатель
engine: AsyncEngine = create_async_engine(settings_db.database_url,
                                          echo=settings_db.DB_ECHO_LOG,
                                          pool_pre_ping=True,)

# 2. Фабрика асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# 3. Зависимость для внедроения в routes


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

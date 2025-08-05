# app/core/config/database/no_class.py

# from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import (create_async_engine,
                                    async_sessionmaker,
                                    AsyncEngine,
                                    AsyncSession)
from app.core.config.database.db_config import settings_db

""" no class way """
# DATABASE_URL = settings_db.database_url
# engine = create_async_engine(DATABASE_URL)
# async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

# 1. Engine
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

async_session_maker = AsyncSessionLocal  # delete
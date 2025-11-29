# app/arq_worker.py

import asyncio
from arq import create_pool
from arq.connections import RedisSettings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config.database.db_config import settings_db
from app.support.parser.orchestrator import ParserOrchestrator
from app.support.parser.model import Name


# Настройка БД
engine = create_async_engine(settings_db.database_url, echo=False, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def parse_rawdata_task(ctx, name_id: int):
    async with AsyncSessionLocal() as session:
        name = await session.get(Name, name_id)
        if not name:
            return {"status": "error", "reason": "Name not found"}
        orchestrator = ParserOrchestrator(session)
        success = await orchestrator._fill_rawdata_for_name(name)
        if success:
            await session.commit()
            return {"status": "success", "name_id": name_id}
        else:
            await session.rollback()
            return {"status": "failed", "name_id": name_id}


# Класс настроек (согласно документации arq)
class WorkerSettings:
    functions = [parse_rawdata_task]
    redis_settings = RedisSettings(host='redis', port=6379)
    on_startup = None
    on_shutdown = None

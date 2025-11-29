# app/arq_worker.py

import asyncio
from arq import create_pool
from arq.connections import RedisSettings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import uuid
from datetime import datetime, timezone
from app.core.config.database.db_config import settings_db
from app.core.config.project_config import settings
from app.support.parser.orchestrator import ParserOrchestrator
from app.support.parser.model import Name, TaskLog


# Настройка БД
engine = create_async_engine(settings_db.database_url, echo=False, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def parse_rawdata_task(ctx, name_id: int):
    # 1. Создаём запись о начале задачи
    task_log = TaskLog(
        task_name="parse_rawdata_task",
        task_id=ctx.get("job_id", str(uuid.uuid4())),
        status="started",
        entity_id=name_id,
        started_at=datetime.utcnow()
    )
    async with AsyncSessionLocal() as session:
        session.add(task_log)
        await session.commit()
        log_id = task_log.id

    try:
        # 2. Таймаут на выполнение всей задачи
        async with asyncio.timeout(settings.ARQ_TASK_TIMEOUT):  # Python 3.11+
            async with AsyncSessionLocal() as session:
                name = await session.get(Name, name_id)
                if not name:
                    raise ValueError("Name not found")

                orchestrator = ParserOrchestrator(session)
                success = await orchestrator._fill_rawdata_for_name(name)
                if success:
                    await session.commit()
                else:
                    await session.rollback()
                    raise RuntimeError("Failed to fill rawdata")
    except Exception as e:
        # 3. Логируем ошибку и НЕ повторяем попытки (останавливаем)
        error_msg = str(e)
        async with AsyncSessionLocal() as session:
            task_log = await session.get(TaskLog, log_id)
            task_log.status = "failed"
            task_log.error = error_msg
            task_log.finished_at = datetime.now(timezone.utc)
            await session.commit()

        # Отменяем повторные попытки
        raise RuntimeError(f"Task failed permanently: {error_msg}") from e
    else:
        # 4. Успешное завершение
        async with AsyncSessionLocal() as session:
            task_log = await session.get(TaskLog, log_id)
            task_log.status = "success"
            task_log.finished_at = datetime.now(timezone.utc)
            await session.commit()


# Класс настроек (согласно документации arq)
class WorkerSettings:
    functions = [parse_rawdata_task]
    redis_settings = RedisSettings(host='redis', port=6379)
    on_startup = None
    on_shutdown = None
    max_tries = settings.ARQ_MAX_TRIES  # 3 попытки, потом — не повторять

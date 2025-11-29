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
    job_id = ctx.get("job_id")
    if not job_id:
        job_id = str(uuid.uuid4())

    # Создаём запись о старте
    async with AsyncSessionLocal() as session:
        task_log = TaskLog(
            task_name="parse_rawdata_task",
            task_id=job_id,
            status="started",
            entity_id=name_id,
            started_at=datetime.now(timezone.utc)
        )
        session.add(task_log)
        await session.commit()
        task_log_id = task_log.id

    try:
        async with asyncio.timeout(settings.ARCQ_TASK_TIMEOUT):
            async with AsyncSessionLocal() as session:
                # Проверка отмены перед началом
                task_log = await session.get(TaskLog, task_log_id)
                if task_log and task_log.cancel_requested:
                    raise asyncio.CancelledError("Task was cancelled by user")

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
    except asyncio.CancelledError:
        async with AsyncSessionLocal() as session:
            task_log = await session.get(TaskLog, task_log_id)
            if task_log:
                task_log.status = "cancelled"
                task_log.finished_at = datetime.now(timezone.utc)
                await session.commit()
        return {"status": "cancelled", "name_id": name_id}
    except Exception as e:
        async with AsyncSessionLocal() as session:
            task_log = await session.get(TaskLog, task_log_id)
            if task_log:
                task_log.status = "failed"
                task_log.error = str(e)
                task_log.finished_at = datetime.now(timezone.utc)
                await session.commit()
        raise

    else:
        async with AsyncSessionLocal() as session:
            task_log = await session.get(TaskLog, task_log_id)
            if task_log:
                task_log.status = "success"
                task_log.finished_at = datetime.now(timezone.utc)
                await session.commit()
        return {"status": "success", "name_id": name_id}


# Класс настроек (согласно документации arq)
class WorkerSettings:
    functions = [parse_rawdata_task]
    redis_settings = RedisSettings(host='redis', port=6379)
    on_startup = None
    on_shutdown = None
    max_tries = settings.ARQ_MAX_TRIES  # 3 попытки, потом — не повторять

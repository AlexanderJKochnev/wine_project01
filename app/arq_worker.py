# app/arq_worker.py

import asyncio
import os
from asyncio import sleep
from fastapi import HTTPException
import random
from arq.connections import RedisSettings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import uuid
from app.core.config.database.db_config import settings_db
from app.core.config.project_config import settings
from app.support.parser.orchestrator import ParserOrchestrator
from app.support.parser.model import Name
from app.core.utils.email_sender import EmailSender


# Настройка БД
engine = create_async_engine(settings_db.database_url, echo=False, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
min_delay = settings.ARQ_MIN_DELAY
max_delay = settings.ARQ_MAX_DELAY
metrics = {
    'completed_tasks': 0
}


async def parse_rawdata_task(ctx, name_id: int):
    try:
        random.seed()
        delay = random.uniform(min_delay, max_delay)
        print(f'{delay=}')
        await sleep(delay)
        job_id = ctx.get("job_id")
        if not job_id:
            job_id = str(uuid.uuid4())
        # Create session for logging the task start
        async with asyncio.timeout(settings.ARQ_TASK_TIMEOUT):
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
    except HTTPException as http_exc:
        if http_exc.status_code in [503, 404]:
            await send_error_notification(f'{str(http_exc)}. '
                                          f'Пропускаем запись, продолжаем работу',
                                          'Уведомление - ошибка 503')
        else:
            raise http_exc
    except Exception as e:
        count = ctx['metrics']['completed_tasks']
        if '503 Service' in str(e):
            await send_error_notification(
                f'{str(e)}. '
                f'Пропускаем запись, продолжаем работу', 'Уведомление - ошибка 503'
            )
        else:
            await send_error_notification(f'{str(e)}. Всего выполнено задач этим воркером: {count}')
            os._exit(1)


async def on_startup_handle(ctx):
    ctx['metrics'] = metrics
    print(f"Воркер запущен. Начальное количество задач: {ctx['metrics']['completed_tasks']}")


async def on_job_post_run_handle(ctx):
    # Увеличиваем счетчик
    ctx['metrics']['completed_tasks'] += 1

    # Выводим текущее значение счетчика в консоль
    count = ctx['metrics']['completed_tasks']
    print(f"[{ctx['job_id']}] Задача завершена. Всего выполнено задач этим воркером: {count}")


# Хук вызывается при остановке процесса воркера
async def on_shutdown_handle(ctx):
    count = ctx['metrics']['completed_tasks']
    print(f"Воркер остановлен. Всего выполнено задач: {count}")
    await send_error_notification(f"Воркер остановлен. Всего выполнено задач: {count}")


async def send_error_notification(error_message: str, subject: str = "Ошибка воркера ARQ"):
    """
    Отправляет уведомление об ошибке на email
    """
    email_sender = EmailSender()
    to_email = settings.EMAIL_ADMIN  # Email address to send error notifications to
    subject = "Ошибка воркера ARQ"
    body = f"Произошла ошибка при выполнении задачи воркера ARQ:\n\n{error_message}"

    await email_sender.send_email(to_email, subject, body)


# Класс настроек (согласно документации arq)
class WorkerSettings:
    functions = [parse_rawdata_task]
    queue_name = 'parse_rawdata_queue'  # Separate queue for this worker
    host = settings.REDIS_HOST
    port = settings.REDIS_PORT
    redis_settings = RedisSettings(host=host, port=port)
    conn_timeout = 10,  # таймаут подключения
    conn_retries = 5,  # попытки переподключения
    conn_retry_delay = 1,  # задержка между попытками
    on_startup = on_startup_handle
    on_shutdown = on_shutdown_handle
    on_job_end = on_job_post_run_handle
    max_tries = settings.ARQ_MAX_TRIES  # 3 попытки, потом — не повторять

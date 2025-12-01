# app/rawdata_arq_worker.py
# Separate worker for processing Rawdata records - parsing HTML and updating field keys

import asyncio
import os
from asyncio import sleep
import json
from arq.connections import RedisSettings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
import uuid
from app.core.config.database.db_config import settings_db
from app.core.config.project_config import settings
from app.support.parser.model import Rawdata
from app.support.parser.utils.html_parser import parse_html_to_dict
from app.support.field_keys.service import FieldKeyService
from app.core.utils.email_sender import EmailSender


# Настройка БД
engine = create_async_engine(settings_db.database_url, echo=False, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
metrics = {
    'completed_tasks': 0
}


async def parse_all_rawdata_task(ctx):
    """
    Parse all Rawdata records, extract key-value pairs, store in parsed_data field,
    and update field keys in the field_keys table.
    """
    try:
        job_id = ctx.get("job_id")
        if not job_id:
            job_id = str(uuid.uuid4())
        
        async with asyncio.timeout(settings.ARQ_TASK_TIMEOUT):
            async with AsyncSessionLocal() as session:
                # Get all Rawdata records that have body_html
                stmt = select(Rawdata).where(Rawdata.body_html.isnot(None))
                result = await session.execute(stmt)
                rawdata_records = result.scalars().all()
                
                print(f"Found {len(rawdata_records)} Rawdata records to process")
                
                for i, rawdata_record in enumerate(rawdata_records):
                    print(f"Processing record {i+1}/{len(rawdata_records)} with id {rawdata_record.id}")
                    
                    # Parse the HTML content
                    parsed_dict, field_mapping = parse_html_to_dict(rawdata_record.body_html)
                    
                    # Store the parsed data as JSON in the parsed_data field
                    if parsed_dict:
                        rawdata_record.parsed_data = json.dumps(parsed_dict, ensure_ascii=False, indent=2)
                    
                    # Process field keys and update the field_keys table
                    for short_name, full_name in field_mapping.items():
                        # Truncate short_name to 25 characters if needed
                        if len(short_name) > 25:
                            short_name = short_name[:25]
                        
                        # Create or update field key
                        field_key_service = FieldKeyService(session)
                        await field_key_service.get_or_create_field_key(
                            short_name=short_name,
                            full_name=full_name
                        )
                    
                    # Commit changes for this record
                    await session.commit()
                    
                    # Small delay to prevent overwhelming the system
                    await sleep(0.01)
                
                print(f"Successfully processed {len(rawdata_records)} Rawdata records")
    
    except Exception as e:
        count = ctx['metrics']['completed_tasks']
        await send_error_notification(f'{str(e)}. Всего выполнено задач этим воркером: {count}')
        os._exit(1)


async def on_startup_handle(ctx):
    ctx['metrics'] = metrics
    print(f"Rawdata processing воркер запущен. Начальное количество задач: {ctx['metrics']['completed_tasks']}")


async def on_job_post_run_handle(ctx):
    # Увеличиваем счетчик
    ctx['metrics']['completed_tasks'] += 1

    # Выводим текущее значение счетчика в консоль
    count = ctx['metrics']['completed_tasks']
    print(f"[{ctx['job_id']}] Задача завершена. Всего выполнено задач этим воркером: {count}")


# Хук вызывается при остановке процесса воркера
async def on_shutdown_handle(ctx):
    count = ctx['metrics']['completed_tasks']
    print(f"Rawdata processing воркер остановлен. Всего выполнено задач: {count}")
    await send_error_notification(f"Rawdata processing воркер остановлен. Всего выполнено задач: {count}")


async def send_error_notification(error_message: str):
    """
    Отправляет уведомление об ошибке на email
    """
    email_sender = EmailSender()
    to_email = settings.EMAIL_ADMIN  # Email address to send error notifications to
    subject = "Ошибка воркера ARQ (Rawdata processing)"
    body = f"Произошла ошибка при выполнении задачи воркера ARQ (Rawdata processing):\n\n{error_message}"

    await email_sender.send_email(to_email, subject, body)


# Класс настроек (согласно документации arq) для Rawdata processing worker
class RawdataWorkerSettings:
    functions = [parse_all_rawdata_task]
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
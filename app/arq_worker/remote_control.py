from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel
from arq import create_pool
from arq.connections import RedisSettings
from app.core.config.project_config import settings
from app.arq_worker import parse_rawdata_task


router = APIRouter(prefix="/arq-worker", tags=["ARQ Worker Remote Control"])


class TaskRequest(BaseModel):
    name_id: int
    job_id: Optional[str] = None


@router.post("/start-task")
async def start_parse_rawdata_task(task_request: TaskRequest):
    """
    Запускает задачу parse_rawdata_task воркера ARQ
    """
    redis_settings = RedisSettings(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    arq_pool = await create_pool(redis_settings)
    
    try:
        if task_request.job_id:
            job = await arq_pool.enqueue_job("parse_rawdata_task", task_request.name_id, _job_id=task_request.job_id)
        else:
            job = await arq_pool.enqueue_job("parse_rawdata_task", task_request.name_id)
        
        return {"message": "Task started successfully", "job_id": job.job_id if job else "unknown"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start task: {str(e)}")
    finally:
        await arq_pool.close()


@router.get("/health")
async def worker_health():
    """
    Проверяет работоспособность воркера ARQ
    """
    redis_settings = RedisSettings(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    arq_pool = await create_pool(redis_settings)
    
    try:
        # Проверяем подключение к Redis
        await arq_pool.ping()
        return {"status": "healthy", "message": "ARQ worker is ready to process tasks"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Worker health check failed: {str(e)}")
    finally:
        await arq_pool.close()
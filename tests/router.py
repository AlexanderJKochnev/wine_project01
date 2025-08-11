# tests/router.py
from fastapi import APIRouter
import asyncio
# from app.core.config.database.db_helper import db_help

router = APIRouter(prefix='/tests',
                   tags=['Проверка соединения с базой данных'])


@router.get("/", summary='Проверка соединения с базой данных')
async def get_answer():
    async def wait_some_time(seconds: float):
        await asyncio.sleep(seconds)  # Не блокирует поток
        return {"waited": seconds}

# app.core.utils.tricks.py
"""
    вспомогательное получение данных из базы данных
    вынесено в отдельный модуль что бы не попасть на циклические ссылки
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.support.ollama.model import ISOLanguage


async def get_lang2_by_name(session: AsyncSession) -> dict:
    """
        возвращает словарь {'English': 'en', ...}
    """
    model = ISOLanguage
    query = select(model.name_en, model.iso_639_1)
    resp = await session.execute(query)
    return dict(resp.all())

async def get_name_by_lang2(session: AsyncSession) -> dict:
    """
        возвращает словарь {'en': 'English', ...}
    """
    model = ISOLanguage
    query = select(model.iso_639_1, model.name_en)
    resp = await session.execute(query)
    return dict(resp.all())

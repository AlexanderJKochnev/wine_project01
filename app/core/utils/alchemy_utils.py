import re
from typing import List, Optional, Tuple

from fastapi import Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.base_model import Base
from app.core.repositories.sqlalchemy_repository import ModelType


async def mass_delete(query: Query, batch: int, session: AsyncSession):
    """
    Удаляет любое большое количество записей с применением ORM-логики
    :param query: запрос на выборку записей которые следует удалить, должен содержать первичный ключ
    :type query:
    :param batch: количество записей в пакете
    :type batch:  int
    :param session: асинхронная сессия
    :type session: AsyncSession
    :return: количество удаленных записей
    :rtype:
    """
    result = session.scalars(query).yield_per(batch)
    icount = 0
    for obj in result:
        await session.delete(obj)
        icount += 1
    await session.commit()
    return icount


def model_to_dict(obj, seen=None):
    if seen is None:
        seen = set()
    if obj is None:
        return None

    obj_id = f"{obj.__class__.__name__}_{id(obj)}"
    if obj_id in seen:
        return None  # защита от циклов
    seen.add(obj_id)

    result = {}
    for key in obj.__dict__.keys():
        if key.startswith("_"):
            continue
        value = getattr(obj, key)
        if isinstance(value, list):
            result[key] = [model_to_dict(item, seen) for item in value]
        elif hasattr(value, "__table__"):  # ORM-объект
            result[key] = model_to_dict(value, seen)
        else:
            result[key] = value
    return result


def get_models() -> List[ModelType]:
    return (cls for cls in Base.registry._class_registry.values() if
            isinstance(cls, type) and hasattr(cls, '__table__'))


def parse_unique_violation(error_msg: str) -> Optional[Tuple[str, str]]:
    """
    Парсит сообщение об ошибке уникальности и извлекает:
    - название поля (constraint)
    - значение, которое вызвало конфликт

    Пример:
    Input: 'duplicate key value violates unique constraint "ix_foods_name"
            DETAIL: Key (name)=(Game (venison)) already exists.'
    Output: ('name', 'Game (venison)')
    """
    # Паттерны для извлечения информации
    patterns = [
        # Для PostgreSQL
        r'Key \((.+?)\)=\((.+?)\) already exists',
        r'duplicate key value violates unique constraint ".+?"\s+DETAIL:\s+Key \((.+?)\)=\((.+?)\)',
        # Для других СУБД
        r'UNIQUE constraint failed: (.+?)\.(.+?)',
        r'Duplicate entry \'(.+?)\' for key \'(.+?)\''
    ]

    for pattern in patterns:
        match = re.search(pattern, error_msg, re.IGNORECASE)
        if match:
            if len(match.groups()) == 2:
                return match.group(1), match.group(2)

    return None

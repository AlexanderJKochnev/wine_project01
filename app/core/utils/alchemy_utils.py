from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Query


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

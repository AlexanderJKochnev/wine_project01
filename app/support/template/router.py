# app/support/template/router.py
"""
замени Template на имя модели в единственном числе с сохранением регистра
проверь словари lbl и paging
"""
from fastapi import APIRouter, Depends, HTTPException, Query
# from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.config.database.db_noclass import get_db
from app.core.config.project_config import get_paging
from app.core.routers.router import create_find_router
from app.support.template.repository import TemplateRepository as repo
from app.support.template.models import Template as MyModel
from app.support.template.schemas import SRead
from app.support.template.schemas import SAdd
from app.support.template.schemas import SUpd
from app.support.template.schemas import SList
from app.support.template.schemas import SDel


# список подсказок, в дальнейшем загрузить в бд на разных языках и выводить на языке интерфейса
lbl: dict = {'get': 'Список категорий напитков',
             'prefix': 'Категории напитков',
             'item': 'Категория',
             'items': 'Категории',
             'notfound': 'не найден(а)'}
paging: dict = get_paging

router = APIRouter(prefix='/templates',
                   tags=[f'{lbl.get("prefix")}'])


# ————————————————————————
# GET: Список с пагинацией
# ————————————————————————
@router.get("/", summary=lbl.get('get'), response_model=SList)
async def get_list(db: AsyncSession = Depends(get_db),
                   page: int = Query(1, ge=1),
                   page_size: int = Query(paging.get('def', 20),
                                          ge=paging.get('min', 1),
                                          le=paging.get('max', 100))
                   ):
    skip = (page - 1) * page_size
    result = await repo.get_all(db, skip=skip, limit=page_size)
    # Общее количество
    total = await db.scalar(select(func.count()).select_from(MyModel))

    return {"items": result,
            "page": page,
            "page_size": page_size,
            "total": total,
            "has_next": skip + len(result) < total,
            "has_prev": page > 1}


# ————————————————————————
# GET: Получение по ID
# ————————————————————————
@router.get("/{item_id}", response_model=SRead)
async def get_one(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await repo.get_by_id(db, item_id)
    if not item:
        raise HTTPException(404, f"{lbl.get('item')} {item_id} {lbl.get('notfound')}")
    return SRead.model_validate(item, from_attributes=True)


# ————————————————————————
# PATCH: Частичное обновление
# ————————————————————————
@router.patch("/{item_id}", response_model=SRead)
async def update_item(
    item_id: int,
    data: SUpd,
    db: AsyncSession = Depends(get_db)
):
    update_data = data.model_dump(exclude_unset=True)  # только переданные поля
    item = await repo.update(db, item_id, update_data)
    if not item:
        raise HTTPException(404, f"{lbl.get('item')} {item_id} {lbl.get('notfound')}")
    return SRead.model_validate(item, from_attributes=True)


# ————————————————————————
# DELETE: Удаление
# ————————————————————————
@router.delete("/{item_id}", response_model=SDel)
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    success = await repo.delete(db, item_id)
    if not success:
        raise HTTPException(404, f"{lbl.get('item')} {item_id} {lbl.get('notfound')}")
    return {"id": item_id, "success": True}


# ————————————————————————
# POST: Создание
# ————————————————————————
@router.post("/", response_model=SRead, status_code=201)
async def create_item(
    data: SAdd,
    db: AsyncSession = Depends(get_db)
):
    result = await repo.create(db, data.model_dump())
    # return result
    return SRead.model_validate(result, from_attributes=True)


# ————————————————————————
# FIND: Поиск по полям (фильтрация)
# ————————————————————————
# find_route = create_find_router(repo=repo, model=repo.model, ReadSchema=SRead)
# router.routes.append(find_route)

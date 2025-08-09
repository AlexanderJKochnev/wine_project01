# app/support/drink/router.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.config.database.db_noclass import get_db
from app.core.config.project_config import get_paging
# from app.core.routers.router import create_find_router
from app.support.drink.repository import DrinkRepository
from app.support.drink.models import Drink as MyModel
from app.support.drink.schemas import SRead
from app.support.drink.schemas import SAdd
from app.support.drink.schemas import SUpd
from app.support.drink.schemas import SList
from app.support.drink.schemas import SDel
from app.support.drink.schemas import SDetail
from app.core.utils import apply_relationship_loads

# список подсказок, в дальнейшем загрузить в бд на разных языках и выводить на языке интерфейса
lbl: dict = {'get': 'Список напитков',
             'prefix': 'Напитки',
             'item': 'Напиток',
             'items': 'Напитки',
             'notfound': 'не найден(а)'}
paging: dict = get_paging

router = APIRouter(prefix='/drinks',
                   tags=[f'{lbl.get("prefix")}'])
repo = DrinkRepository()

# ————————————————————————
# GET: Список с пагинацией
# ————————————————————————
@router.get("/", summary=lbl.get('get'), response_model=SList)
async def get_list(session: AsyncSession = Depends(get_db),
                   page: int = Query(1, ge=1),
                   page_size: int = Query(paging.get('def', 20),
                                          ge=paging.get('min', 1),
                                          le=paging.get('max', 100))):
    skip = (page - 1) * page_size
    result = await repo.get_all(skip, page_size, session)
    return result


# ————————————————————————
# GET: Получение по ID
# ————————————————————————
@router.get("/{item_id}", response_model=SRead)
async def get_one(item_id: int, db: AsyncSession = Depends(get_db)):
    print(f'{type(repo)=}')
    item = await repo.get_by_id(item_id, db)
    if not item:
        raise HTTPException(404, f"{lbl.get('item')} {item_id} {lbl.get('notfound')}")
    # return SRead.model_validate(item, from_attributes=True)
    return item


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
# DETAIL: детальная информация с загрузкой relationships
# ————————————————————————


@router.get("/detail/", response_model=List[SDetail])
async def get_details(db: AsyncSession = Depends(get_db)):
    """
    Возвращает данные с раскрытыми полями из связанных таблиц:
    """
    stmt = select(MyModel)
    stmt = apply_relationship_loads(stmt, MyModel)
    res = await db.scalars(stmt)
    results = res.all()

    # Конвертируем в схему
    return [
        SDetail.model_validate(
            result,
            from_attributes=True,
            # При необходимости можно добавить контекст
        )
        for result in results
    ]


@router.get("/detail/{user_id}", response_model=SDetail)
async def get_detail(item_id: int, db: AsyncSession = Depends(get_db)):
    """То же, но по ID"""
    stmt = select(MyModel).where(MyModel.id == item_id)
    stmt = apply_relationship_loads(stmt, MyModel)
    res = await db.scalars(stmt)
    result = res.first()
    if not result:
        raise HTTPException(404, "Result not found")
    return SDetail.model_validate(result, from_attributes=True)

# ————————————————————————
# FIND: Поиск по полям (фильтрация) динамический роутер
# ————————————————————————
# find_route = create_find_router(repo=repo, model=repo.model, ReadSchema=SRead)
# router.routes.append(find_route)

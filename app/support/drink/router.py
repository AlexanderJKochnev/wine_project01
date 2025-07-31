# app/support/drink/router.py
from fastapi import APIRouter, Depends  # noqa: F401

from app.support.drink.repository import DrinkRepository
from app.support.drink.schemas import SDrink, SDrinkAdd
from app.support.drink.service import DrinkDAO

# from sqlalchemy import select   # noqa: F401
# from app.core.config.database.db_helper import db_helper     # noqa: F401
# from app.support.template.models import TemplateModel     # noqa: F401
# from app.core.config.database.db_noclass import async_session_maker


tag1: str = 'Работа с напитками'
tag2: str = 'Получить все напитки'
prefix = '/drink'
router = APIRouter(prefix=f'{prefix}', tags=[f'{tag1}'])


@router.get("/", summary=tag2, response_model=list[SDrink])
async def get_all_drink(
        request_body:
        DrinkRepository = Depends()) -> list[SDrink]:
    result = await DrinkDAO.find_all(**request_body.to_dict())
    # return result
    if result:
        return result
    else:
        return {'message': 'Напитки не найдены!'}


@router.get("/{id}", summary="Получить один напиток по id")
async def get_drink_by_id(drink_id: int) -> SDrink | dict:
    # result = await DrinkDAO.find_one_or_none_by_id(drink_id)
    result = await DrinkDAO.find_full_data(drink_id)
    if result:
        return result
    else:
        return {'message': f'Напиток с ID {drink_id} не найден!'}


@router.get("/filter_by", summary="Получить один напиток по фильтру")
async def get_drink_by_filter(request_body: DrinkRepository =
                              Depends()) -> SDrink | dict:
    result = await DrinkDAO.find_one_or_none(**request_body.to_dict())
    if result:
        return result
    else:
        return {'message': 'Напиток с указанными параметрами не найден!'}


@router.post("/add/")
async def create_drink(drink: SDrinkAdd) -> dict:
    check = await DrinkDAO.add(**drink.dict())
    if check:
        return {"message": "Напиток успешно добавлен!",
                "drink": drink}
    else:
        return {"message": "Ошибка при добавлении напитка!"}


@router.put("/update/")
async def update_category_description(drink: SDrinkAdd) -> dict:
    check = await DrinkDAO.update(
        filter_by={'title': drink.title,
                   'subtitle': drink.subtitle},
        **drink.dict())
    # category_description=category.category_description)
    if check:
        return {"message": f"Описание напитка {drink.title}"
                           f"{drink.subtitle} успешно обновлено!",
                "drink": drink}
    else:
        return {"message": "Ошибка при обновлении описания напитка!"}


@router.delete("/del/{drink_id}")
async def delete_category(drink_id: int) -> dict:
    # filter_by: dict = {a: b for a, b in category.dict().items() if b}
    check = await DrinkDAO.delete(id=drink_id)
    if check:
        return {"message": f"напиток {drink_id} "
                           f"удален!"}
    else:
        return {"message": "Ошибка при удалении напитка!"}

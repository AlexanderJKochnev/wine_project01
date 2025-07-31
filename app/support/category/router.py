from fastapi import APIRouter, Depends

from app.support.category.repository import CategoryRepository
from app.support.category.schemas import SCategory, SCategoryAdd, SCategoryUpd
from app.support.category.service import CategoryDAO
# from typing import Literal
router = APIRouter(prefix='/categories',
                   tags=['Работа с категориями напитков'])


@router.get("/", summary='Список категорий напитков')
async def get_all_categories(
        request_body:
        CategoryRepository = Depends()) -> (list[SCategory] | dict):
    result = await CategoryDAO.find_all(**request_body.to_dict())
    if result:
        return result
    else:
        return {'message': 'Категории не найдены!'}


@router.post("/add/")
async def create_category(category: SCategoryAdd) -> dict:
    check = await CategoryDAO.add(**category.dict())
    if check:
        return {"message": "Категория успешно добавлена!",
                "category": category}
    else:
        return {"message": "Ошибка при добавлении категории!"}


@router.put("/update_description/")
async def update_category_description(category: SCategoryUpd) -> dict:
    check = await CategoryDAO.update(
        filter_by={'category_name': category.category_name},
        **category.dict())
    # category_description=category.category_description)
    if check:
        return {"message": "Описание категории успешно обновлено!",
                "category": category}
    else:
        return {"message": "Ошибка при обновлении описания категории!"}


@router.delete("/del/{category_id}")
async def delete_category(category_id: int) -> dict:
    # filter_by: dict = {a: b for a, b in category.dict().items() if b}
    check = await CategoryDAO.delete(id=category_id)
    if check:
        return {"message": f"Категория {category_id} "
                           f"удалена!"}
    else:
        return {"message": "Ошибка при удалении категории!"}

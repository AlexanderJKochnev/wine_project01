# app/support/item/router_item_view.py
"""
    роутер для ListView и DetailView для модели Item
    выводит плоские словари с локализованными полями
    по языкам
"""
from typing import List
from fastapi import Request, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config.database.db_async import get_db
from app.core.schemas.base import PaginatedResponse
from app.support.item.service import ItemService
from app.support.item.repository import ItemRepository
from app.support.item.model import Item
from app.support.item.schemas import ItemListView, ItemDetailView


class ItemViewRouter:
    def __init__(self, prefix: str = '/items_view', tags: List[str] = None):
        from fastapi import APIRouter
        self.router = APIRouter()
        self.prefix = prefix
        self.tags = tags or ["items_view"]
        self.paginated_response = PaginatedResponse[ItemListView]
        self.setup_routes()

    def setup_routes(self):
        """Настройка маршрутов для ListView и DetailView"""
        # Маршрут для получения списка элементов с пагинацией
        self.router.add_api_route(
            "/list/{lang}",
            self.get_list,
            methods=["GET"],
            response_model=List[ItemListView],
            tags=self.tags,
            summary="Получить список элементов с локализацией"
        )

        # Маршрут для получения списка элементов с пагинацией
        self.router.add_api_route(
            "/list_paginated/{lang}",
            self.get_list_paginated,
            methods=["GET"],
            response_model=PaginatedResponse[ItemListView],
            tags=self.tags,
            summary="Получить список элементов с пагинацией и локализацией"
        )

        # Маршрут для получения одного элемента по id с локализацией
        self.router.add_api_route(
            "/detail/{lang}/{id}",
            self.get_detail,
            methods=["GET"],
            response_model=ItemDetailView,
            tags=self.tags,
            summary="Получить детальную информацию по элементу с локализацией"
        )

    async def get_list(self, lang: str, session: AsyncSession = Depends(get_db)):
        """Получить список элементов с локализацией"""
        service = ItemService()
        items = await service.get_list_view(lang, ItemRepository, Item, session)
        return items

    async def get_list_paginated(self,
                                 lang: str,
                                 page: int = Query(1, ge=1, description="Номер страницы"),
                                 page_size: int = Query(20, ge=1, le=100, description="Размер страницы"),
                                 session: AsyncSession = Depends(get_db)):
        """Получить список элементов с пагинацией и локализацией"""
        service = ItemService()
        result = await service.get_list_view_page(page, page_size, ItemRepository, Item, session)
        return result

    async def get_detail(self, lang: str, id: int, session: AsyncSession = Depends(get_db)):
        """Получить детальную информацию по элементу с локализацией"""
        service = ItemService()
        item = await service.get_detail_view(lang, id, ItemRepository, Item, session)
        if not item:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail=f"Item with id {id} not found")
        print(f'{type(item)=}')
        result = ItemDetailView(**item)
        # result = {key: val for key, val in item.items() if val}

        return result.model_dump(exclude_none=True, exclude_unset=True)

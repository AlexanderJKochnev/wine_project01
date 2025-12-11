# app/support/item/router_item_view.py
"""
    роутер для ListView и DetailView для модели Item
    выводит плоские словари с локализованными полями
    по языкам
"""
from typing import List
from fastapi import Request, Depends, Query, Path
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
        # Маршрут для получения списка элементов без пагинации
        self.router.add_api_route(
            "/list/{lang}",
            self.get_list,
            methods=["GET"],
            # response_model=List[ItemListView],
            tags=self.tags,
            summary="Получить список элементов с локализацией"
        )

        # Маршрут для получения списка элементов с пагинацией
        self.router.add_api_route(
            "/list_paginated/{lang}",
            self.get_list_paginated,
            methods=["GET"],
            # response_model=PaginatedResponse[ItemListView],
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

        # 2 Маршрут для поиска элементов по полям title* и subtitle* связанной модели Drink
        self.router.add_api_route(
            "/search_by_drink/{lang}",
            self.search_by_drink_title_subtitle_paginated,
            methods=["GET"],
            # response_model=PaginatedResponse[ItemListView],
            tags=self.tags,
            summary="Поиск элементов по полям title* и subtitle* связанной модели Drink"
        )

        # Маршрут для поиска элементов с использованием триграммного индекса
        self.router.add_api_route(
            "/search_trigram/{lang}",
            self.search_by_trigram_index,
            methods=["GET"],
            response_model=PaginatedResponse[ItemListView],
            tags=self.tags,
            summary="Поиск элементов по триграммному индексу в связанной модели Drink"
        )

    async def get_list(self, lang: str = Path(..., description="Язык локализации"), session: AsyncSession = Depends(get_db)):
        """Получить список элементов с локализацией"""
        service = ItemService()
        result = await service.get_list_view(lang, ItemRepository, Item, session)

        return result

    async def get_list_paginated(self,
                                 lang: str = Path(..., description="Язык локализации"),
                                 page: int = Query(1, ge=1, description="Номер страницы"),
                                 page_size: int = Query(20, ge=1, le=100, description="Размер страницы"),
                                 session: AsyncSession = Depends(get_db)):
        """Получить список элементов с пагинацией и локализацией"""
        service = ItemService()
        result = await service.get_list_view_page(page, page_size, ItemRepository, Item, session, lang)
        # self.paginated_response

        return result

    async def get_detail(self, lang: str = Path(..., description="Язык локализации"), id: int = Path(..., description="ID элемента"), session: AsyncSession = Depends(get_db)):
        """Получить детальную информацию по элементу с локализацией"""
        service = ItemService()
        item = await service.get_detail_view(lang, id, ItemRepository, Item, session)
        if not item:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail=f"Item with id {id} not found")
        print(f'{type(item)=}')

        # Create ItemDetailView instance
        result = ItemDetailView(**item)

        # Return the model dump with empty values removed
        return result.model_dump(exclude_none=True, exclude_unset=True)

    async def search_by_drink_title_subtitle_paginated(self,
                                                       lang: str = Path(..., description="Язык локализации"),
                                                       search: str = Query(
                                                           ..., description="Строка для поиска в полях title* и subtitle* модели Drink"),
                                                       page: int = Query(1, ge=1, description="Номер страницы"),
                                                       page_size: int = Query(
                                                           20, ge=1, le=100, description="Размер страницы"),
                                                       session: AsyncSession = Depends(get_db)):
        """Поиск элементов по полям title* и subtitle* связанной модели Drink с пагинацией"""
        service = ItemService()
        skip = (page - 1) * page_size
        limit = page_size
        items, total = await service.search_by_drink_title_subtitle(
            search, lang, ItemRepository, Item, session, skip, limit
        )

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_next": skip + len(items) < total,
            "has_prev": page > 1
        }

    async def search_by_trigram_index(self,
                                      lang: str = Path(..., description="Язык локализации"),
                                      search_str: str = Query(
                                          None, description="Строка для поиска в триграммном индексе модели Drink"),
                                      page: int = Query(1, ge=1, description="Номер страницы"),
                                      page_size: int = Query(15, ge=1, le=100, description="Размер страницы"),
                                      session: AsyncSession = Depends(get_db)):
        """Поиск элементов с использованием триграммного индекса в связанной модели Drink"""
        service = ItemService()
        skip = (page - 1) * page_size
        limit = page_size

        items, total = await service.search_by_trigram_index(
            search_str, lang, ItemRepository, Item, session, skip, limit
        )

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_next": skip + len(items) < total,
            "has_prev": page > 1
        }

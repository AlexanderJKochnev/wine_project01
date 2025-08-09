# app/core/routers/base_router.py

from typing import Type, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
# from sqlalchemy.orm import selectinload
from app.core.config.database.db_noclass import get_db
from app.core.schemas.base_schema import BaseSchema
from app.core.repositories.sqlalchemy_repo2 import Repository as repo
from app.core.config.project_config import get_paging


class BaseRouter:
    """
    Базовый роутер с общими CRUD-методами.
    Наследуйте и переопределяйте get_query() для добавления selectinload.
    """

    def __init__(
        self,
        model: Type[Any],
        create_schema: Type[BaseSchema],
        update_schema: Type[BaseSchema],
        read_schema: Type[BaseSchema],
        prefix: str,
        tags: List[str],
        session: AsyncSession = Depends(get_db)
    ):
        self.model = model
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.read_schema = read_schema
        self.prefix = prefix
        self.tags = tags
        self.router = APIRouter(prefix=prefix, tags=tags)
        self.session = session  # будет установлен через зависимости
        self.paging = get_paging
        self.setup_routes()

        def get_query(self):
            """
            Переопределяемый метод.
            Возвращает select() с нужными selectinload.
            По умолчанию — без связей.
            """
            return select(self.model)

        async def get_session(self, session: AsyncSession = Depends(get_db)):
            """Зависимость для сессии"""
            self.session = session
            return session

        def setup_routes(self):
            """Настраивает маршруты"""
            self.router.add_api_route("", self.create, methods=["POST"], response_model=self.read_schema)
            self.router.add_api_route("", self.get_all, methods=["GET"], response_model=Any)  # см. ниже
            self.router.add_api_route("/{item_id}", self.get_one, methods=["GET"], response_model=self.read_schema)
            self.router.add_api_route("/{item_id}", self.update, methods=["PATCH"], response_model=self.read_schema)
            self.router.add_api_route("/{item_id}", self.delete, methods=["DELETE"], response_model=dict)

        async def get_one(self, item_id: int, session: AsyncSession = Depends(get_session)) -> Any:
            obj = await repo.get_by_id(item_id, session)
            if not obj:
                raise HTTPException(status_code=404, detail=f"{self.model.__name__} not found")
            return obj

        async def get_all(self, page: int = Query(1, ge=1),
                          page_size: int = Query(self.paging.get('def', 20),
                                                 ge=self.paging.get('min', 1),
                                                 le=self.paging.get('max', 1000)),
                          session: AsyncSession = Depends(get_session)) -> dict:
            skip = (page - 1) * page_size
            result = await repo.get_all(skip=skip, limit=page_size, session=session)
            return result

        async def create(self, data: Any, session: AsyncSession = Depends(get_session)) -> Any:
            obj = await repo.create(data, session)
            return obj

        async def update(
                self, id: int, data: Any, session: AsyncSession = Depends(get_session)) -> Any:
            obj = await repo.update(id, data, session)
            if not obj:
                raise HTTPException(status_code=404, detail="Not found")
            return obj

        async def delete(
                self, id: int, session: AsyncSession = Depends(get_session)) -> dict:
            obj = await repo.delete(id, session)
            await session.delete(obj)
            await session.commit()
            return {"success": True, "message": f"{self.model.__name__} deleted"}

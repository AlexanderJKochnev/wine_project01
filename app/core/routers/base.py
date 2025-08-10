# app/core/routers/base.py

from typing import Type, Any, List, TypeVar, Generic
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import create_model
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.config.database.db_noclass import get_db
from app.core.schemas.base import BaseSchema
from app.core.config.project_config import get_paging
from app.core.schemas.base import DeleteResponse, PaginatedResponse

paging = get_paging
TCreate = TypeVar("TCreate", bound=BaseSchema)
TUpdate = TypeVar("TUpdate", bound=BaseSchema)
TRead = TypeVar("TRead", bound=BaseSchema)


class BaseRouter(Generic[TCreate, TUpdate, TRead]):
    """
    Базовый роутер с общими CRUD-методами.
    Наследуйте и переопределяйте get_query() для добавления selectinload.
    """

    def __init__(
        self,
        model: Type[Any],
        repo: Type[Any],
        create_schema: Type[TCreate],
        update_schema: Type[TUpdate],
        read_schema: Type[TRead],
        prefix: str,
        tags: List[str],
        session: AsyncSession = Depends(get_db)
    ):
        self.model = model
        self.repo = repo()
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.read_schema = read_schema
        self.prefix = prefix
        self.tags = tags
        self.router = APIRouter(prefix=prefix, tags=tags)
        self.session = session  # будет установлен через зависимости
        self.paginated_response = create_model(f"Paginated{read_schema.__name__}",
                                               __base__=PaginatedResponse[read_schema])
        self.delete_response = DeleteResponse
        # self.setup_routes()

    def get_query(self):
        """
            Переопределяемый метод.
            Возвращает select() с нужными selectinload.
            По умолчанию — без связей.
        """
        return select(self.model)

    """ async def get_sesion(self, session: AsyncSession = Depends(get_db)):
        # Зависимость для сессии
        self.session = session
        return session
    """

    def setup_routes(self):
        """Настраивает маршруты"""
        self.router.add_api_route("", self.create, methods=["POST"], response_model=self.create_schema)
        self.router.add_api_route("", self.get_all, methods=["GET"], response_model=self.paginated_response)
        self.router.add_api_route("/{item_id}", self.get_one, methods=["GET"], response_model=self.read_schema)
        self.router.add_api_route("/{item_id}", self.update, methods=["PATCH"], response_model=self.read_schema)
        self.router.add_api_route("/{item_id}", self.delete, methods=["DELETE"], response_model=self.delete_response)

    async def get_one(self, item_id: int, session: AsyncSession = Depends(get_db)) -> TRead:
        obj = await self.repo.get_by_id(item_id, session=session)
        if not obj:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} not found")
        return obj

    async def get_all(self, page: int = Query(1, ge=1),
                      page_size: int = Query(paging.get('def', 20),
                                             ge=paging.get('min', 1),
                                             le=paging.get('max', 1000)),
                      session: AsyncSession = Depends(get_db)) -> dict:
        skip = (page - 1) * page_size
        items = await self.repo.get_all(skip=skip, limit=page_size, session=session)
        # Подсчёт общего количества
        count_stmt = select(func.count()).select_from(self.model)
        count_result = await session.execute(count_stmt)
        total = count_result.scalar()
        page = (skip // page_size) + 1
        retu = {"items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "has_next": skip + len(items) < total,
                "has_prev": page > 1}
        result = self.paginated_response(**retu)
        return result

    async def create(self, data: Any, session: AsyncSession = Depends(get_db)) -> TRead:
        obj = await self.repo.create(data.model_dump(exclude_unset=True), session)
        return obj

    async def update(self, id: int, data: TUpdate,
                     session: AsyncSession = Depends(get_db)) -> TRead:
        obj = await self.repo.update(id, data.model_dump(exclude_unset=True), session)
        if not obj:
            raise HTTPException(status_code=404, detail="Not found")
        return obj

    async def delete(self, id: int,
                     session: AsyncSession = Depends(get_db)) -> DeleteResponse:
        result = await self.repo.delete(id, session)
        if result:
            return {"success": True, "message": f"{self.model.__name__} deleted"}
        else:
            raise HTTPException(status_code=404, detail="Not found")

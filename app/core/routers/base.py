# app/core/routers/base.py

from typing import Type, Any, List, TypeVar
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import create_model
from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
from app.core.config.database.db_async import get_db
from app.core.schemas.base import BaseSchema
from app.core.config.project_config import get_paging
from app.core.schemas.base import DeleteResponse, PaginatedResponse

paging = get_paging
TCreate = TypeVar("TCreate", bound=BaseSchema)
TUpdate = TypeVar("TUpdate", bound=BaseSchema)
TRead = TypeVar("TRead", bound=BaseSchema)


class BaseRouter:
    """
    Базовый роутер с общими CRUD-методами.
    Наследуйте и переопределяйте get_query() для добавления selectinload.
    """

    def __init__(
        self,
        model: Type[Any],
        repo: Type[Any],
        create_schema: Type[BaseSchema],
        update_schema: Type[BaseSchema],
        read_schema: Type[BaseSchema],
        prefix: str,
        tags: List[str]
        # session: AsyncSession = Depends(get_db)
    ):
        self.model = model
        self.repo = repo()
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.read_schema = read_schema
        self.prefix = prefix
        self.tags = tags
        self.router = APIRouter(prefix=prefix, tags=tags)
        # self.session = session  # будет установлен через зависимости
        self.paginated_response = create_model(f"Paginated{read_schema.__name__}",
                                               __base__=PaginatedResponse[read_schema])
        self.delete_response = DeleteResponse
        # self.setup_routes()

    def setup_routes(self):
        """Настраивает маршруты"""
        self.router.add_api_route("", self.create, methods=["POST"], response_model=self.create_schema)
        self.router.add_api_route("", self.get_all, methods=["GET"], response_model=self.paginated_response)
        self.router.add_api_route("/{item_id}", self.get_one, methods=["GET"], response_model=self.read_schema)
        self.router.add_api_route("/{item_id}", self.update, methods=["PATCH"], response_model=self.read_schema)
        self.router.add_api_route("/{item_id}", self.delete, methods=["DELETE"], response_model=self.delete_response)

    async def get_one(self, id: int, session: AsyncSession = Depends(get_db)) -> Any:
        try:
            obj = await self.repo.get_by_id(id, session)
            if not obj:
                raise HTTPException(status_code=404, detail=f"{self.model.__name__} not found")
            return obj
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {str(e)}"
            )

    async def get_all(self, page: int = Query(1, ge=1),
                      page_size: int = Query(paging.get('def', 20),
                                             ge=paging.get('min', 1),
                                             le=paging.get('max', 1000)),
                      session: AsyncSession = Depends(get_db)) -> dict:
        try:
            skip = (page - 1) * page_size
            items = await self.repo.get_all(skip=skip, limit=page_size, session=session)
            # Подсчёт общего количества
            total = await self.repo.get_count(session)
            page = (skip // page_size) + 1
            retu = {"items": items,
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "has_next": skip + len(items) < total,
                    "has_prev": page > 1}
            result = self.paginated_response(**retu)
            return result
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching data: {str(e)}"
            )

    async def create(self, data: TCreate, session: AsyncSession = Depends(get_db)) -> TRead:
        try:
            data_dict = data.model_dump(exclude_unset=True)
            print(f"Attempting to create: {data_dict}")
            print(f'{data_dict=}')
            obj = await self.repo.create(data.model_dump(exclude_unset=True), session)
            print(f"Successfully created: {obj}")
            return obj
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=f"{self.model.__name__} already exists"
            )
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Validation error: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating {self.model.__name__}: {str(e)}"
            )

    async def update(self, id: int, data: TUpdate,
                     session: AsyncSession = Depends(get_db)) -> TRead:
        try:
            obj = await self.repo.update(id, data.model_dump(exclude_unset=True), session)
            if not obj:
                raise HTTPException(status_code=404, detail="Not found")
            return obj
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Validation error: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating {self.model.__name__}: {str(e)}"
            )

    async def delete(self, id: int,
                     session: AsyncSession = Depends(get_db)) -> DeleteResponse:
        try:
            result = await self.repo.delete(id, session)
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{self.model.__name__} with id {id} not found"
                )
            return {'success': result,
                    'deleted_count': 1,
                    'message': f'{self.model.__name__} with id {id} has been deleted'}
            # return Response(status_code=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting {self.model.__name__}: {str(e)}"
            )

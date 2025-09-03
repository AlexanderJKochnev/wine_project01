# app/core/routers/base.py

from typing import Type, Any, List, TypeVar, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import create_model
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
from app.core.config.database.db_async import get_db
from app.core.schemas.base import ReadSchema
from app.core.config.project_config import get_paging
from app.core.schemas.base import DeleteResponse, PaginatedResponse
from app.auth.dependencies import get_current_active_user
from app.core.services.logger import logger
from app.core.services.service import Service


paging = get_paging
TCreate = TypeVar("TCreate", bound=ReadSchema)
TUpdate = TypeVar("TUpdate", bound=ReadSchema)
TRead = TypeVar("TRead", bound=ReadSchema)


class BaseRouter:
    """
    Базовый роутер с общими CRUD-методами.
    Наследуйте и переопределяйте get_query() для добавления selectinload.
    """

    def __init__(
        self,
        model: Type[Any],
        repo: Type[Any],
        create_schema: Type[ReadSchema],
        patch_schema: Type[ReadSchema],
        read_schema: Type[ReadSchema],
        prefix: str,
        tags: List[str]
        # session: AsyncSession = Depends(get_db)
    ):
        self.model = model
        self.repo = repo()
        self.service = Service(self.repo, self.model)
        self.create_schema = create_schema
        self.patch_schema = patch_schema
        self.read_schema = read_schema
        self.prefix = prefix
        self.tags = tags
        self.router = APIRouter(prefix=prefix, tags=tags, dependencies=[Depends(get_current_active_user)])
        # self.session = session  # будет установлен через зависимости
        self.paginated_response = create_model(f"Paginated{read_schema.__name__}",
                                               __base__=PaginatedResponse[read_schema])
        self.delete_response = DeleteResponse
        self.responses = {404: {"description": "Record not found",
                                "content": {"application/json": {"example": {"detail": "Record with id 1 not found"}}}}}

        # self.setup_routes()

    def setup_routes(self):
        """Настраивает маршруты"""
        self.router.add_api_route("", self.create, methods=["POST"], response_model=self.read_schema)
        self.router.add_api_route("", self.get, methods=["GET"], response_model=self.paginated_response)
        self.router.add_api_route("/search", self.search, methods=["GET"],
                                  response_model=self.paginated_response)
        self.router.add_api_route("/deepsearch", self.deep_search, methods=["GET"],
                                  response_model=self.paginated_response)
        self.router.add_api_route("/advsearch", self.advanced_search, methods=["GET"],
                                  response_model=self.paginated_response)
        self.router.add_api_route("/{id}",
                                  self.get_one, methods=["GET"],
                                  response_model=self.read_schema,
                                  # responses=self.responses
                                  )
        self.router.add_api_route("/{id}", self.patch, methods=["PATCH"], response_model=self.read_schema)
        self.router.add_api_route("/{id}", self.delete, methods=["DELETE"], response_model=self.delete_response)

    async def get_one(self,
                      # id: int = Query(..., description="ID", gt=0),
                      id: int,
                      session: AsyncSession = Depends(get_db)) -> Any:
        """
            Получение одной записи по ID с четким разделением ошибок:
            - 400: Неверный формат ID или параметры
            - 404: Запись не найдена
            - 500: Внутренняя ошибка сервера
            """
        obj = await self.service.get_by_id(id, session)
        if obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} с ID {id} не найден"
            )
        return obj  # self.read_schema.model_validate(obj)

    async def get(self, page: int = Query(1, ge=1),
                  page_size: int = Query(paging.get('def', 20),
                                         ge=paging.get('min', 1),
                                         le=paging.get('max', 1000)),
                  session: AsyncSession = Depends(get_db)) -> dict:
        try:
            response = await self.service.get_all(page, page_size, session)
            result = self.paginated_response(**response)
            return result
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching data: {str(e)}"
            )

    async def create(self, data: TCreate, session: AsyncSession = Depends(get_db)) -> TRead:
        try:
            obj = await self.service.create(data, session)
            return obj
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=f"{self.model.__name__} already exists"
            )
        except ValidationError as e:
            raise HTTPException(
                status_code=401, detail=f"Validation error: {str(e)}"
                # status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Validation error: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating {self.model.__name__}: {str(e)}"
            )

    async def patch(self, id: int, data: TUpdate,
                    session: AsyncSession = Depends(get_db)) -> TRead:
        try:
            obj = await self.service.patch(id, data, session)
            if not obj:
                raise HTTPException(status_code=404, detail="Not found")
            return obj
        except Exception as e:
            logger.warning(f"HTTP error PATCH: {e}")

    async def delete(self, id: int,
                     session: AsyncSession = Depends(get_db)) -> DeleteResponse:
        result = await self.repo.delete(id, session)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} with id {id} not found"
            )
        return {'success': result,
                'deleted_count': 1 if result else 0,
                'message': f'{self.model.__name__} with id {id} has been deleted'}

    async def search(self, query: str = Query(...),
                     page: int = Query(1, ge=1),
                     page_size: int = Query(paging.get('def', 20),
                                            ge=paging.get('min', 1),
                                            le=paging.get('max', 1000)),
                     session: AsyncSession = Depends(get_db)) -> dict:
        """Поиск по всем текстовым полям основной таблицы"""
        items = await self.service.search_in_main_table(query, page, page_size, session=session)
        result = self.paginated_response(**items)
        return result

    async def deep_search(self, query: Optional[str] = Query(None),
                          session: AsyncSession = Depends(get_db)) -> dict:
        """Поиск по текстовым полям основной таблицы и связанных таблиц"""
        # return await service.deep_search_in_main_table(query)
        pass

    async def advanced_search(self, query: Optional[str] = Query(None),
                              # service: Service = Depends(),
                              session: AsyncSession = Depends(get_db)) -> dict:
        """Расширенный поиск по произвольным текстовым полям"""
        # return await service.advanced_search_in_main_table(query)
        pass

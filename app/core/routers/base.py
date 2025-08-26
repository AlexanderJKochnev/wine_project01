# app/core/routers/base.py

from typing import Type, Any, List, TypeVar, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import create_model
from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
from app.core.config.database.db_async import get_db
from app.core.schemas.base import ReadSchema
from app.core.config.project_config import get_paging
from app.core.schemas.base import DeleteResponse, PaginatedResponse
from app.auth.dependencies import get_current_active_user


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
        update_schema: Type[ReadSchema],
        read_schema: Type[ReadSchema],
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
        self.router = APIRouter(prefix=prefix, tags=tags, dependencies=[Depends(get_current_active_user)])
        # self.session = session  # будет установлен через зависимости
        self.paginated_response = create_model(f"Paginated{read_schema.__name__}",
                                               __base__=PaginatedResponse[read_schema])
        self.delete_response = DeleteResponse
        # self.setup_routes()

    def setup_routes(self):
        """Настраивает маршруты"""
        self.router.add_api_route("", self.create, methods=["POST"], response_model=self.read_schema)
        self.router.add_api_route("", self.get, methods=["GET"], response_model=self.paginated_response)
        self.router.add_api_route("/a", self.get_one, methods=["GET"], response_model=self.read_schema)
        self.router.add_api_route("/a", self.update, methods=["PATCH"], response_model=self.read_schema)
        self.router.add_api_route("/a", self.delete, methods=["DELETE"], response_model=self.delete_response)

    async def get_one(self,
                      id: Optional[int] = Query(..., description="ID", gt=0),
                      session: AsyncSession = Depends(get_db)) -> Any:
        """
            Получение одной записи по ID с четким разделением ошибок:
            - 400: Неверный формат ID или параметры
            - 404: Запись не найдена
            - 500: Внутренняя ошибка сервера
            """
        try:
            # Получаем объект из репозитория
            obj = await self.repo.get_by_id(id, session)
            # Четкое разделение: объект не найден = 404
            if obj is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{self.model.__name__} с ID {id} не найден"
                )
            return obj
        except HTTPException as he:
            # Логируем HTTP ошибки (кроме 404, которые могут быть частыми)
            if he.status_code != status.HTTP_404_NOT_FOUND:
                # logger.warning(f"HTTP error in get_one: {he.detail}")
                raise he

        except ValueError as e:
            # Ошибки валидации (неверный формат данных)
            # logger.warning(f"Validation error in get_one: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Неверный формат параметров: {e}")
        except Exception:
            # Все остальные ошибки = внутренняя ошибка сервера
            # logger.error(f"Unexpected error in get_one: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Внутренняя ошибка сервера. Попробуйте позже."
            )

    async def get(self, page: int = Query(1, ge=1),
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
            # if isinstance(data, dict):
            #     data_dict = {key: val for key, val in data.items() if val}
            # else:
            data_dict = data.model_dump(exclude_unset=True)
            obj = await self.repo.create(data_dict, session)
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

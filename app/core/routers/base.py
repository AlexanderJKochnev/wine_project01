# app/core/routers/base.py

import logging
from typing import Any, List, Type, TypeVar
from dateutil.relativedelta import relativedelta
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
# from pydantic import create_model
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

# from app.auth.dependencies import get_current_active_user
from app.auth.dependencies import get_active_user_or_internal
# from pydantic import ValidationError
from app.core.config.database.db_async import get_db
from app.core.config.project_config import get_paging, settings
from app.core.utils.common_utils import back_to_the_future
from app.core.schemas.base import (DeleteResponse, PaginatedResponse, ReadSchema,
                                   CreateResponse, UpdateSchema, CreateSchema)
from app.core.utils.pydantic_utils import PyUtils as py
from app.core.services.service import Service
from app.core.exceptions import (ValidationException, ConflictException, NotFoundException)


paging = get_paging
TCreateSchema = TypeVar("TCreateSchema", bound=CreateSchema)
TUpdateSchema = TypeVar("TUpdateSchema", bound=UpdateSchema)
TReadSchema = TypeVar("TReadSchema", bound=ReadSchema)
TCreateResponse = TypeVar("TCreateResponse", bound=CreateResponse)
TUpdateSchema = TypeVar("TUpdateSchema", bound=UpdateSchema)
dev = settings.DEV
logger = logging.getLogger(__name__)
delta = (datetime.now(timezone.utc) - relativedelta(years=2)).isoformat()


class BaseRouter:
    """
    Базовый роутер с общими CRUD-методами.
    Наследуйте и переопределяйте get_query() для добавления selectinload.
    """

    def __init__(
        self,
        model: Type[Any],
        repo: Type[Any],
        prefix: str,
        tags: List[str],
        create_schema: Type[ReadSchema],
        path_schema: Type[UpdateSchema],
        read_schema: Type[ReadSchema],
        create_response_schema: Type[CreateResponse],
        create_schema_relation: Type[CreateResponse],
        service: Service,
        # session: AsyncSession = Depends(get_db)
    ):
        self.model = model
        self.repo = repo
        self.service = service
        self.create_schema = create_schema
        self.read_schema = read_schema
        self.create_schema_relation = create_schema_relation
        self.create_response_schema = create_response_schema
        self.prefix = prefix
        self.tags = tags

        self.read_response = py.read_response(read_schema)
        self.paginated_response = py.paginated_response(read_schema)
        # self.non_paginated_response = py.non_paginated_response(read_schema)
        self.delete_response = DeleteResponse
        self.responses = {404: {"description": "Record not found",
                                "content": {"application/json": {"example": {"detail": "Record with id 1 not found"}}}}}
        self.router = APIRouter(prefix=prefix, tags=tags, dependencies=[Depends(get_active_user_or_internal)])
        # self.router = APIRouter(prefix=prefix, tags=tags, dependencies=[Depends(get_current_active_user)])
        self.setup_routes()
        self.service = service
        self.path_schema = path_schema

    def setup_routes(self):
        """Настраивает маршруты"""
        self.router.add_api_route("", self.create, methods=["POST"], response_model=self.create_response_schema)

        self.router.add_api_route("/hierarchy",
                                  self.create_relation,
                                  status_code=status.HTTP_200_OK,
                                  methods=["POST"],
                                  response_model=self.read_response)
        # get all без паггинации
        self.router.add_api_route("", self.get, methods=["GET"], response_model=self.paginated_response)
        # search с пагинацией
        self.router.add_api_route("/search", self.search, methods=["GET"],
                                  response_model=self.paginated_response)
        # search без пагинации
        self.router.add_api_route(
            "/search_all", self.search_all, methods=["GET"], response_model=List[self.read_schema])
        # get without pagination
        self.router.add_api_route("/all", self.get_all, methods=["GET"], response_model=List[self.read_response])
        # get one buy id
        self.router.add_api_route("/{id}",
                                  self.get_one, methods=["GET"],
                                  response_model=self.read_schema,
                                  )
        self.router.add_api_route("/{id}", self.patch, methods=["PATCH"], response_model=self.create_response_schema)
        self.router.add_api_route("/{id}", self.delete, methods=["DELETE"], response_model=self.delete_response)

    async def create(self, data: TCreateSchema, session: AsyncSession = Depends(get_db)) -> TReadSchema:
        """
        Создание одной записи без зависимостей - удалить в production
        """
        try:
            # obj = await self.service.create(data, self.repo, self.model, session)
            obj = await self.service.get_or_create(data, self.repo, self.model, session)
            return obj
        except ValidationException as e:
            await session.rollback()
            logger.warning(f"Validation error in create_item: {e}")
            raise HTTPException(
                status_code=501,  # status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"ValidationException. Validation error in create_item: {e}")

        except ConflictException as e:
            await session.rollback()
            logger.warning(f"Conflict in create_item: {e}")
            raise HTTPException(
                status_code=502,  # status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"ConflictException. Conflict in create_item: {e}"
            )

        except IntegrityError as e:
            await session.rollback()
            logger.error(f"Integrity error in create_item: {e}")
            raise HTTPException(
                status_code=503,  # status.HTTP_400_BAD_REQUEST, detail="Data integrity error"
                detail=f'IntgrityError. {e}'
            )

        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Database error in create_item: {e}")
            raise HTTPException(
                status_code=504,  # status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"SQLAlchemyError. Database error in create_item: {e}"
            )

        except Exception as e:
            await session.rollback()
            logger.error(f"Unexpected error in create_item: {e}")
            raise HTTPException(
                status_code=505,  # status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
                detail=f'UnexpectedError, {e}'
            )

    async def create_relation(self, data: TCreateSchema, session: AsyncSession = Depends(get_db)) -> TReadSchema:
        """
        Создание одной записи с зависимостями - если в таблице есть зависимости
        они будут рекурсивно найдены в связанных таблицах (или добавлены при отсутсвии)
        """
        try:
            # obj = await self.service.create(data, self.model, session)
            obj = await self.service.create_relation(data, self.repo, self.model, session)
            return await self.service.get_by_id(obj.id, self.repo, self.model, session)
        except ValidationException as e:
            await session.rollback()
            logger.warning(f"Validation error in create_item: {e}")
            raise

        except ConflictException as e:
            await session.rollback()
            logger.warning(f"Conflict in create_item: {e}")
            raise

        except IntegrityError as e:
            await session.rollback()
            logger.error(f"Integrity error in create_item: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Data integrity error"
            )

        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Database error in create_item: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error {e}"
            )

        except Exception as e:
            await session.rollback()
            logger.error(f"Unexpected error in create_item: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error {e}"
            )

    async def patch(self, id: int, data: TUpdateSchema,
                    session: AsyncSession = Depends(get_db)) -> TReadSchema:
        """
            Изменение одной записи по id
        """
        try:
            existing_item = await self.service.get_by_id(id, self.repo, self.model, session)
            if not existing_item:
                raise NotFoundException(detail=f"Item with id {id} not found")
            obj = await self.service.patch(existing_item, data, self.repo, session)

            if not obj:
                await session.rollback()
                raise NotFoundException(detail=f"Item with id {id} not found")
            # await session.commit()
            # await session.refresh(obj)
            return obj
        except ValidationException as e:
            await session.rollback()
            logger.warning(f"Validation error in update_item: {e}")
            raise

        except IntegrityError as e:
            await session.rollback()
            logger.error(f"Integrity error in update_item: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Data integrity error"
            )

        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Database error in update_item: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
            )

        except Exception as e:
            await session.rollback()
            logger.error(f"Unexpected error in update_item: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
            )

    async def delete(self, id: int,
                     session: AsyncSession = Depends(get_db)) -> DeleteResponse:
        """
            Удаление одной записи по id
        """
        try:
            existing_item = await self.service.get_by_id(id, self.repo, self.model, session)
            if not existing_item:
                raise NotFoundException(detail=f"Item with id {id} not found")
            result = await self.service.delete(existing_item, self.repo, session)
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete item"
                )
            resu = {'success': result, 'deleted_count': 1 if result else 0,
                    'message': f'{self.model.__name__} with id {id} has been deleted'}
            return DeleteResponse(**resu)
        except NotFoundException:
            raise

        except SQLAlchemyError as e:
            logger.error(f"Database error in delete_item: {e}")

            # Проверяем, является ли ошибка связанной с внешними ключами
            if "foreign key constraint" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail="Cannot delete item due to existing references"
                )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
            )

        except Exception as e:
            logger.error(f"Unexpected error in delete_item: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
            )

    async def get_one(self,
                      id: int,
                      session: AsyncSession = Depends(get_db)) -> TReadSchema:
        """
            Получение одной записи по ID
        """
        try:
            obj = await self.service.get_by_id(id, self.repo, self.model, session)
            if obj is None:
                raise NotFoundException(detail=f"Item with id {id} not found")
            return obj  # self.read_schema.model_validate(obj)
        except NotFoundException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"record with id {id} not found")

        except SQLAlchemyError as e:
            logger.error(f"Database error in get_item: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

        except Exception as e:
            logger.error(f"Unexpected error in get_item: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
            )

    async def get(self,
                  after_date: datetime = Query(delta,
                                               description="Дата в формате ISO 8601 (например, 2024-01-01T00:00:00Z)"),
                  page: int = Query(1, ge=1),
                  page_size: int = Query(paging.get('def', 20),
                                         ge=paging.get('min', 1),
                                         le=paging.get('max', 1000)),
                  session: AsyncSession = Depends(get_db)
                  ) -> PaginatedResponse:
        """
        Получение постранично всех записей после заданной даты.
        По умолчанию задана дата - 2 года от сейчас
        """
        # print(f"📥 GET request for {self.model.__name__} from")
        try:
            after_date = back_to_the_future(after_date)
            response = await self.service.get_all(after_date, page, page_size, self.repo, self.model, session)
            return response
            result = self.paginated_response(**response)
            return result
        except Exception as e:
            logger.error(f"Unexpected error in get: {e} {self.model.__name__}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Internal server error")

    async def get_all(self, after_date: datetime = Query(
        (datetime.now(timezone.utc) - relativedelta(years=2)).isoformat(),
        description="Дата в формате ISO 8601 (например, 2024-01-01T00:00:00Z)"
    ), session: AsyncSession = Depends(get_db)) -> List[TReadSchema]:
        """
        Получение все записей одним списком после указанной даты.
        По умолчанию задана дата - 2 года от сейчас
        """
        try:
            after_date = back_to_the_future(after_date)
            return await self.service.get(after_date, self.repo, self.model, session)
        except Exception as e:
            logger.error(f"Unexpected error in get: {e} {self.model.__name__}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Internal server error")

    async def search(self,
                     search: str,
                     page: int = Query(1, ge=1),
                     page_size: int = Query(paging.get('def', 20),
                                            ge=paging.get('min', 1),
                                            le=paging.get('max', 1000)),
                     session: AsyncSession = Depends(get_db)) -> PaginatedResponse:
        """
            Поиск по всем текстовым полям основной таблицы
            с постраничным выводом результата
        """
        return await self.service.search(search, page, page_size, self.repo, self.model, session)

    async def search_all(self,
                         search: str,
                         session: AsyncSession = Depends(get_db)) -> List[TReadSchema]:
        """
            Поиск по всем текстовым полям основной таблицы
            с постраничным выводом результата
        """
        return await self.service.search_all(search, self.repo, self.model, session)

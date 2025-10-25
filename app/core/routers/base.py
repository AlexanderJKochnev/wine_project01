# app/core/routers/base.py

import logging
from typing import Any, List, Type, TypeVar, Optional
from dateutil.relativedelta import relativedelta
from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_active_user_or_internal
from app.core.config.database.db_async import get_db
from app.core.config.project_config import get_paging, settings
from app.core.utils.common_utils import back_to_the_future
from app.core.schemas.base import (DeleteResponse, PaginatedResponse, ReadSchema,
                                   CreateResponse, UpdateSchema, CreateSchema)
from app.core.utils.pydantic_utils import PyUtils as py
from app.core.services.service import Service
from app.core.exceptions import exception_to_http


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
        Создание одной записи без зависимостей
        """
        try:
            # obj = await self.service.create(data, self.repo, self.model, session)
            obj = await self.service.get_or_create(data, self.repo, self.model, session)
            return obj
        except Exception as e:
            await session.rollback()
            raise exception_to_http(e)

    async def create_relation(self, data: TCreateSchema, session: AsyncSession = Depends(get_db)) -> TReadSchema:
        """
        Создание одной записи с зависимостями - если в таблице есть зависимости
        они будут рекурсивно найдены в связанных таблицах (или добавлены при отсутсвии)
        """
        try:
            # obj = await self.service.create(data, self.model, session)
            obj = await self.service.create_relation(data, self.repo, self.model, session)
            return await self.service.get_by_id(obj.id, self.repo, self.model, session)
        except Exception as e:
            await session.rollback()
            logger.error(f"Unexpected error in create_item: {e}")
            raise exception_to_http(e)

    async def patch(self, id: int, data: TUpdateSchema,
                    session: AsyncSession = Depends(get_db)) -> TReadSchema:
        """
            Изменение одной записи по id
        """
        try:
            existing_item = await self.service.get_by_id(id, self.repo, self.model, session)
            if not existing_item:
                raise Exception(f'NOT_FOUND: Реадктируемая запись {id} не найдена на сервере')
            obj = await self.service.patch(existing_item, data, self.repo, session)
            if not obj:
                await session.rollback()
                raise Exception(f'NOT_FOUND: Отредактированная запись {id} не найдена на сервере. изменения отменены')
            return obj
        except Exception as e:
            # добавить обработку SQLALCHEMY
            await session.rollback()
            raise exception_to_http(e)

    async def delete(self, id: int,
                     session: AsyncSession = Depends(get_db)) -> DeleteResponse:
        """
            Удаление одной записи по id
        """
        existing_item = await self.service.get_by_id(id, self.repo, self.model, session)
        if not existing_item:
            raise HTTPException(status_code=404, detail=f'удаляемая запись {id} не существует')
        try:
            result = await self.service.delete(existing_item, self.repo, session)
        except Exception as e:
            raise HTTPException(status_code=401, detail=e)
        # проверка удаления
        # checking = await self.service.get_by_id(id, self.repo, self.model, session)
        # if checking == existing_item:
        #     raise HTTPException(status_code=500, detail=f'Ошибка удаления записи {id}: {checking}')
        res = {'success': result,
               'deleted_count': 1 if result else 0,
               'message': f'Удалена запись {id}'}
        return res

    async def get_one(self,
                      id: int,
                      session: AsyncSession = Depends(get_db)):
        """
            Получение одной записи по ID
        """
        obj = await self.service.get_by_id(id, self.repo, self.model, session)
        if obj is None:
            raise HTTPException(status_code=404, detail=f'Запрашиваемый файл {id} не найден на сервере')
        return obj

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
        after_date = back_to_the_future(after_date)
        response = await self.service.get_all(after_date, page, page_size, self.repo, self.model, session)
        result = self.paginated_response(**response)
        return result

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
                     search: Optional[str] = None,
                     page: int = Query(1, ge=1),
                     page_size: int = Query(paging.get('def', 20),
                                            ge=paging.get('min', 1),
                                            le=paging.get('max', 1000)),
                     session: AsyncSession = Depends(get_db),
                     ) -> PaginatedResponse:
        """
            Поиск по всем текстовым полям основной таблицы
            с постраничным выводом результата
            все аргументы кроме paging убрать в kwargs
        """
        kwargs: str = {'page': page, 'page_size': page_size}
        if search:
            kwargs['search_str'] = search
        return await self.service.search(self.repo, self.model, session, **kwargs)
        # else:
        #     return await self.get(after_date=datetime.now(timezone.utc) - relativedelta(years=2),
        #                           page=page, page_size=page_size,
        #                           session=session)

    async def search_all(self,
                         search: str = Query(None),
                         session: AsyncSession = Depends(get_db)) -> List[TReadSchema]:
        """
            Поиск по всем текстовым полям основной таблицы
            с постраничным выводом результата
        """
        kwargs: dict = {}
        if search:
            kwargs['search_str'] = search
        return await self.service.search(self.repo, self.model, session, **kwargs)

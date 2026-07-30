# app/core/routers/base.py

# from dateutil.relativedelta import relativedelta
from datetime import datetime
from typing import Any, Callable, List, Type, TypeVar

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_active_user_or_internal, get_current_api_user
from app.core.config.database.db_async import get_db
from app.core.config.project_config import get_paging, settings
from app.core.exceptions import exception_to_http
from app.core.schemas.base import (CreateResponse, CreateSchema, DeleteResponse, PaginatedResponse, ReadSchema,
                                   UpdateSchema)
from app.core.services.service import Service
from app.core.utils.common_utils import back_to_the_future, delta_data, jprint
from app.core.utils.pydantic_utils import get_pyschema, get_repo, get_service, orresponse

paging = get_paging
TCreateSchema = TypeVar("TCreateSchema", bound=CreateSchema)
TUpdateSchema = TypeVar("TUpdateSchema", bound=UpdateSchema)
TReadSchema = TypeVar("TReadSchema", bound=ReadSchema)
TCreateResponse = TypeVar("TCreateResponse", bound=CreateResponse)
TUpdateSchema = TypeVar("TUpdateSchema", bound=UpdateSchema)
TService = TypeVar("TService", bound=Service)

# dev = settings.DEV
delta = delta_data(settings.DATA_DELTA)    # (datetime.now(timezone.utc) - relativedelta(years=2)).isoformat()


def type_checking(result, func_name):
    logger.info(f'{type(result)}, {func_name}')
    if isinstance(result, dict):
        if items := result.get('items'):
            logger.info(f'    {type(items[0])}, {func_name}')
    elif isinstance(result, list):
        logger.info(f'    {type(result[0])}, {func_name}')


class BaseRouter:
    """
    Базовый роутер с общими CRUD-методами.
    Наследуйте и переопределяйте get_query() для добавления selectinload.
    """

    def __init__(
        self,
        model: Type[Any],
        prefix: str,
        auth_dependency: Callable = get_active_user_or_internal,
        # auth_dependency: Callable = get_current_api_user,
        **kwargs
    ):
        self.model = model
        self.repo = get_repo(model)
        self.service: TService = get_service(model)
        self.auth_dependency = auth_dependency
        # input py schema for simple create without relation
        self.create_schema = get_pyschema(model, 'Create')
        self.create_response_schema = get_pyschema(model, 'CreateResponseSchema') or self.create_schema
        # input py schema for create with relation
        self.create_schema_relation = get_pyschema(model, 'CreateRelation') or self.create_schema
        # input update schema
        self.update_schema = dict  # get_pyschema(model, 'Update')
        # response schemas:
        self.read_schema = get_pyschema(model, 'Read')
        self.read_schema_relation = get_pyschema(model, 'ReadRelation') or self.read_schema
        self.paginated_response = PaginatedResponse[self.read_schema_relation]
        self.nonpaginated_response = List[self.read_schema_relation]
        self.delete_response = DeleteResponse

        self.prefix = prefix
        self.tags = [prefix.replace('/', '')]
        include_in_schema = kwargs.get('include_in_schema', True)
        self.router = APIRouter(prefix=prefix,
                                tags=self.tags,
                                dependencies=[Depends(self.auth_dependency)],
                                include_in_schema=include_in_schema)
        """
            action: (path, func, methods: list, schema_name
        """
        self.autoroutes: dict = {'create': ("", self.create, ["POST"], self.create_schema.__name__),
                                 'create_hierarchy': ("/hierarchy", self.create_relation, ["POST"], self.create_schema_relation.__name__),
                                 'get': ("", self.get, ["GET"], None),
                                 'search': ("/search", self.search, ["GET"], None),
                                 'search_all': ("/search_all", self.search_all, ["GET"], None),
                                 'get_all': ("/all", self.get_all, ["GET"], None),
                                 'get_full': ("/full", self.get_full, ["GET"], None),
                                 'list_view': ("/list_view", self.get_list_view_page, ["GET"], None),
                                 'get_one': ("/{id}", self.get_one, ["GET"], None),
                                 'update_or_create': ("", self.update_or_create, ["PATCH"], self.update_schema.__name__),
                                 'patch': ("/{id}", self.patch, ["PATCH"], self.update_schema.__name__),
                                 'delete': ("/{id}", self.delete, ["DELETE"], None)
                                 }

        self.setup_routes()
        # self.read_response = py.read_response(read_schema)
        # self.path_schema = path_schema

    def setup_route_adv(self, *args):
        """ Настройка маршрутов тонкая
            в args через запятую указать какие роуты нужны
            'create', 'get', 'update' ...
            список см self.autoroutes выше
        """
        routes = [val for key, val in self.autoroutes.items() if key in args]
        for path, endpoint, act, schema in routes:
            self.router.add_api_route(path, endpoint, methods=act, openapi_extra={'x-request-schema': schema})

    def setup_route_custom(self, path: str, func, methods: str):
        """
        customized routes setup
        setup_route_custom('/path/{id}', self.func, 'POST,GET', self.create_schema.__name__)
        """
        methods = methods.split(',')
        schema = self.create_schema.__name__ if 'POST' in methods else None
        self.router.add_api_route(path, func, methods=methods, openapi_extra={'x-request-schema': schema})

    def setup_routes(self):
        """Настраивает маршруты"""
        # 1. create simple
        self.router.add_api_route("", self.create, methods=["POST"],
                                  openapi_extra={'x-request-schema': self.create_schema.__name__})
        # 2. create in hierarchy
        self.router.add_api_route("/hierarchy",
                                  self.create_relation,
                                  status_code=status.HTTP_200_OK,
                                  methods=["POST"],
                                  openapi_extra={'x-request-schema': self.create_schema_relation.__name__})
        # 3. get all без паггинации не раньше заданной даты
        self.router.add_api_route("", self.get, methods=["GET"],
                                  openapi_extra={'x-request-schema': None})
        # 4. search с пагинацией (по всем текстовым полям модели, во вложеннных не ищет)
        self.router.add_api_route("/search", self.search, methods=["GET"],
                                  openapi_extra={'x-request-schema': None})
        # 5. search без пагинации (по всем текстовым полям модели, во вложеннных не ищет)
        self.router.add_api_route("/search_all",
                                  self.search_all, methods=["GET"],
                                  openapi_extra={'x-request-schema': None})
        # 6. get without pagination не раньше заданной даты
        self.router.add_api_route("/all",
                                  self.get_all, methods=["GET"],
                                  openapi_extra={'x-request-schema': None})
        # 7. get full list no pagination
        self.router.add_api_route("/full",
                                  self.get_full,
                                  methods=["GET"],
                                  openapi_extra={'x-request-schema': None})
        # 8. list view
        self.router.add_api_route("/list_view",
                                  self.get_list_view_page,
                                  methods=["GET"],
                                  openapi_extra={'x-request-schema': None})
        # 9. get one buy id
        self.router.add_api_route("/{id}",
                                  self.get_one, methods=["GET"],
                                  openapi_extra={'x-request-schema': None})
        # 10. update_or_create
        self.router.add_api_route("",
                                  self.update_or_create, methods=["PATCH"],
                                  openapi_extra={'x-request-schema': self.update_schema.__name__})
        # 11. patch one
        self.router.add_api_route("/{id}",
                                  self.patch, methods=["PATCH"],
                                  openapi_extra={'x-request-schema': self.update_schema.__name__})
        # 12. delete one
        self.router.add_api_route("/{id}",
                                  self.delete, methods=["DELETE"],
                                  openapi_extra={'x-request-schema': None})

    async def create(self, data: TCreateSchema,
                     session: AsyncSession = Depends(get_db)) -> TReadSchema:
        """
        Создание одной записи без зависимостей
        input_valudation_chema <>CreateRelation
        response_model <>CreateResponseSchema
        """
        try:
            obj, created = await self.service.get_or_create(data, self.repo, self.model, session)
            logger.critical('----------------------')
            return orresponse(obj)
        except Exception as e:
            detail = (f'ошибка создания записи {e}, model = {self.model}, '
                      f'create_schema = {self.create_schema}, '
                      f'service = {self.service} ,'
                      f'repository = {self.repo}')
            print(detail)
            raise HTTPException(status_code=500, detail=detail)

    async def batch_create(self, data: List[TCreateSchema],
                           session: AsyncSession = Depends(get_db)) -> List[TReadSchema]:
        """
         Создание нескольких записей без зависимостей DELETE?
        """
        try:
            obj = await self.service.batch_get_or_create(data, self.repo, self.model, session)
            return orresponse(obj)
        except Exception as e:
            detail = (f'ошибка создания записи {e}, model = {self.model}, '
                      f'create_schema = {self.create_schema}, '
                      f'service = {self.service} ,'
                      f'repository = {self.repo}')
            print(detail)
            raise HTTPException(status_code=500, detail=detail)

    async def create_relation(self, data: TCreateSchema, session: AsyncSession = Depends(get_db)) -> TReadSchema:
        """
        Создание одной записи с зависимостями - если в таблице есть зависимости
        они будут рекурсивно найдены в связанных таблицах (или добавлены при отсутсвии)
        переписать если есть зависимости
        input_valudation_chema <>CreateRelation
        response_model <>ReadRelation
        """
        try:
            obj = await self.service.create_relation(data, self.repo, self.model, session)
            if isinstance(obj, tuple):
                obj, _ = obj
            # return obj
            response = await self.service.get_by_id(obj.id, self.repo, self.model, session)
            return orresponse(response)
        except Exception as e:
            raise exception_to_http(e)

    async def update_or_create(self, data: TUpdateSchema, background_tasks: BackgroundTasks,
                               session: AsyncSession = Depends(get_db)) -> TReadSchema:
        """
            обновление / добавление одной записи ? пока нигде не используется
            input_valudation_chema <>CreateRelation
            response_model <>ReadRelation
        """
        try:
            obj, created = await self.service.update_or_create(data, self.repo, self.model, background_tasks, session)
            return orresponse(obj)
        except Exception as e:
            detail = (f'ошибка обновления записи {e}, model = {self.model}, '
                      f'create_schema = {self.create_schema}, '
                      f'service = {self.service} ,'
                      f'repository = {self.repo}')
            print(detail)
            raise HTTPException(status_code=405, detail=detail)

    async def patch(self, id: int,
                    data: dict, background_tasks: BackgroundTasks,
                    session: AsyncSession = Depends(get_db)) -> dict:
        """
            Изменение одной записи по id
            input_valudation_chema dict
            валидация входных данных произойдет уже в репозитории - все что не подходит будет отброшено
            response_model <>Read
        """
        logger.info('router')
        logger.info(f'{data=}')
        result = await self.service.patch(id, data, self.repo, self.model, background_tasks,
                                          session)
        return orresponse(result)

    # @logger.catch(reraise=True)
    async def delete(self, id: int, background_tasks: BackgroundTasks,
                     session: AsyncSession = Depends(get_db)) -> DeleteResponse:
        """
            Удаление одной записи по id
            input_valudation_chema No
            response_model <>DeleteResponse
        """
        try:
            await self.service.delete(id, self.model, self.repo, background_tasks, session)
            return DeleteResponse(success=True, deleted_count=1, message=f'record with {id=}')
        except ValueError:
            raise HTTPException(status_code=404, detail=f"record with {id=} not found")
        except PermissionError as e:
            raise HTTPException(status_code=409, detail=f'{id=}, {str(e)}')
        except Exception as e:
            raise HTTPException(status_code=409, detail=f'{id=}, {str(e)}')

    async def get_one(self,
                      id: int,
                      session: AsyncSession = Depends(get_db)):
        """
            Получение одной записи по ID
            input_valudation_chema <>CreateRelation
            response_model <>ReadRelatio
        """
        response = await self.service.get_by_id(id, self.repo, self.model, session)
        return orresponse(response)

    async def get_by_field(self,
                           field: str = Query(..., description='имя поля'),
                           value: Any = Query(..., description='значение поля'),
                           session: AsyncSession = Depends(get_db)):
        """
            Получение одной записи по значению поля
        """
        filter = {field: value}
        response = await self.service.get_by_field(filter, self.repo, self.model, session)
        return orresponse(response)

    async def get(self, request: Request,
                  after_date: datetime = Query(delta,
                                               description="Дата в формате ISO 8601 (например, 2024-01-01T00:00:00Z)"),
                  page: int = Query(1, ge=1),
                  page_size: int = Query(paging.get('def', 20),
                                         ge=paging.get('min', 1),
                                         le=paging.get('max', 1000)),
                  session: AsyncSession = Depends(get_db)
                  ):
        """
            Получение постранично всех записей после заданной даты.
            По умолчанию задана дата - 2 года от сейчас
            input_valudation_chema None
            response_model PaginatedResponse[<>ReadRelation>]
        """
        after_date = back_to_the_future(after_date)
        response = await self.service.get(after_date, page, page_size, self.repo, self.model, session)
        if response is None:
            raise HTTPException(status_code=404, detail=f'Запрашиваемый файл {id} не найден на сервере')
        return orresponse(response)
        # return response

    async def get_all(
            self, request: Request,
            after_date: datetime = Query(delta,
                                         # (datetime.now(timezone.utc) - relativedelta(years=2)).isoformat(),
                                         description="Дата в формате ISO 8601 (например, 2024-01-01T00:00:00Z)"
                                         ),
            session: AsyncSession = Depends(get_db),
            limit: int = 20
    ):
        """
            Получение все записей одним списком после указанной даты.
            По умолчанию задана дата - 2 года от сейчас
            input_valudation_chema <>CreateRelation
            response_model <>ReadRelatio

        """
        try:
            after_date = back_to_the_future(after_date)
            response = await self.service.get_all(after_date, self.repo, self.model, session)
            return orresponse(response)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Internal server error. {e}")

    async def get_full(self, session: AsyncSession = Depends(get_db), limit: int = 20) -> List[TReadSchema]:
        """
            то же что и get но без ограничения по дате
        """
        try:
            response = await self.service.get_full(self.repo, self.model, session, limit)
            return orresponse(response)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Internal server error. {e}")

    async def get_full_with_pagination(self,
                                       page: int = Query(1, ge=1),
                                       page_size: int = Query(paging.get('def', 20),
                                                              ge=paging.get('min', 1),
                                                              le=paging.get('max', 1000)),
                                       session: AsyncSession = Depends(get_db)
                                       ) -> PaginatedResponse:
        """
            Получение постранично всех записей без ограничения по дате
        """
        # print(f"📥 GET request for {self.model.__name__} from")
        response = await self.service.get_full_with_pagination(page, page_size, self.repo, self.model, session)
        return orresponse(response)
        # type_checking(response, 'get')
        # result = self.paginated_response(**response)
        # return result

    async def search(self, request: Request,
                     search: str = Query(None, description="Поисковый запрос. "
                                         "В случае пустого запроса будут "
                                         "выведены все данные "),
                     page: int = Query(1, ge=1),
                     page_size: int = Query(paging.get('def', 20),
                                            ge=paging.get('min', 1),
                                            le=paging.get('max', 1000)),
                     session: AsyncSession = Depends(get_db),
                     ) -> dict:
        """
            Поиск по всем текстовым полям основной таблицы
            с постраничным выводом результата
            input_valudation_chema None
            response_model PaginatedResponse[<>ReadRelation>]
        """
        result = await self.service.search(request, search, page, page_size, self.repo, self.model, session)
        return orresponse(result)

    async def search_all(self, request: Request,
                         search: str = Query(None, description="Поисковый запрос. "
                                             "В случае пустого запроса будут "
                                             "выведены все данные "),
                         session: AsyncSession = Depends(get_db), limit: int = 20) -> List[TReadSchema]:
        """
            Поиск по всем текстовым полям основной таблицы БЕЗ пагинации
            input_valudation_chema <>CreateRelation
            response_model <>ReadRelatio
        """
        result = await self.service.search_all(request, search, self.repo, self.model, session, limit)
        return orresponse(result)

    async def get_list_view_page(
        self,
            lang: str = Query('en', description='язык для вывода данных'),
            search: str = Query(None, description='поисковый запрос'),
            page: int = Query(1, ge=1),
            page_size: int = Query(paging.get('def', 20),
                                   ge=paging.get('min', 1),
                                   le=paging.get('max', 1000)),
            session: AsyncSession = Depends(get_db)
    ):
        """
            Получение постранично всех записей после заданной даты.
            По умолчанию задана дата - 2 года от сейчас
            input_valudation_chema None
            response_model PaginatedResponse[<>ReadRelation>]
        """
        response = await self.service.get_list_view_page(search, page, page_size, self.repo, self.model, session, lang)
        if response is None:
            raise HTTPException(status_code=404, detail='Запрашиваемые данные не найдены на сервере')
        return orresponse(response)
        # return response


class LightRouter:
    """
        минимальный роутер с зависимостями
    """

    def __init__(self, prefix: str, **kwargs):
        self.prefix = prefix
        self.tags = [prefix.replace('/', '')]
        include_in_schema = kwargs.get('include_in_schema', True)
        self.router = APIRouter(prefix=prefix,
                                tags=self.tags,
                                dependencies=[Depends(get_current_api_user)],
                                # dependencies = [Depends(get_active_user_or_internal)],
                                include_in_schema=include_in_schema
                                )
        # auth_dependency: Callable = get_current_api_user,
        self.setup_routes()

    def setup_routes(self):
        """ override it as follows """
        self.router.add_api_route("", self.endpoints,
                                  methods=["POST"], response_model=self.create_schema)

    async def endpoint(self, request: Request):
        """ override it """

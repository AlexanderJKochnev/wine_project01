# app/main.py
# import os
# import sys
# import logging

# Включаем логирование multiprocessing ДО ВСЕХ ИМПОРТОВ
# logging.basicConfig(level=logging.DEBUG)

# Включаем дебаг multiprocessing
# import multiprocessing
# multiprocessing.util.log_to_stderr(logging.DEBUG)

# Логируем момент создания семафоров
# import multiprocessing.resource_tracker as rt
# rt._DEBUG = True

# print("🔍 Начинаем импорты...")
# print("=" * 60)

# from fastapi import BackgroundTasks
import sys
from contextlib import asynccontextmanager
from time import perf_counter
from typing import List, Optional
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.admin.config import setup_starlette_admin
from app.auth.routers import auth_router, user_router
from app.core.config.database.click_async import ClickHouseManager, get_dump  # , get_ch_client
from app.core.config.database.db_async import DatabaseManager, init_db_extensions
from app.core.config.database.seaweed_async import close_seaweed, init_seaweed
from app.core.config.project_config import settings
from app.core.exceptions import AppBaseException
from app.core.repositories.clickhouse_repository import ClickHouseRepositoryFactory
from app.core.services.translate_service import TranslationService
from app.core.services.vllm_service_manager import ServiceManager
from app.preact.create.router import CreateRouter
from app.preact.delete.router import DeleteRouter
from app.preact.get.router import GetRouter
from app.preact.handbook.router import HandbookRouter
from app.preact.handbook_page.router import HandbookRouterPage
from app.preact.patch.router import PatchRouter
from app.preact.read.router import ReadRouter
from app.support.api.router import ApiRouter
from app.support.category.router import CategoryRouter
from app.support.clickhouse.router import ClickImportRouter
from app.support.country.router import CountryRouter
# from app.support.customer.router import CustomerRouter
from app.support.drink.router import DrinkRouter
from app.support.food.router import FoodRouter
# -------ИМПОРТ РОУТЕРОВ----------
from app.support.gemma.router import GemmaRouter
from app.support.item.router import ItemRouter
from app.support.item.router_item_image import ItemImageRouter
from app.support.item.router_item_view import ItemViewRouter
from app.support.lwin.router import LwinRouter
from app.support.merging.router import MergingRouter
from app.support.ollama.router import ISOLanguageRouter, PromptRouter, ProptionRouter, WriterRuleRouter
from app.support.parcel.router import ParcelRouter, SiteRouter
from app.support.parser.router import (CodeRouter, ImageRouter, NameRouter, OrchestratorRouter, RawdataRouter,
                                       RegistryRouter, StatusRouter)
from app.support.producer.router import ProducerRouter, ProducerTitleRouter
from app.support.region.router import RegionRouter
from app.support.seaweeds.router import SeaweedsRouter
from app.support.source.router import SourceRouter
from app.support.subcategory.router import SubcategoryRouter
from app.support.subregion.router import SubregionRouter
from app.support.superfood.router import SuperfoodRouter
# from app.support.color.router import ColorRouter
from app.support.sweetness.router import SweetnessRouter
from app.support.tasting.router import BaseIngredientRouter, BodyRouter, GlasswareRouter, ScaleRouter, TastingNoteRouter
from app.support.varietal.router import VarietalRouter
from app.support.vintage.router import ClassificationRouter, DesignationRouter, VintageConfigRouter
from app.support.vllm.router import TranslateHelperRouter, TranslateRawDataRouter, VllmRouter

logger.info('start initialisation')

_seaweeds_fids_dump: Optional[List[str]] = None

db_manager = DatabaseManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
        открытие асинхронных соединений с сервисами
    """
    logger.remove()  # Удаляем стандартный обработчик
    std_id = logger.add(
        sys.stdout, colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG", enqueue=True  # ВАЖНО: делает логирование неблокирующим (использует очередь)
    )
    log_id = logger.add("logs/app.log", rotation="100 MB", retention="10 days", compression="zip", enqueue=True)
    logger.success('logger инициализирован')
    # db_manager = DatabaseManager()
    logger.info("Lifespan: Инициализация ресурсов...")

    try:
        await db_manager.check_connection()
        logger.success(f"Lifespan: PostgreSQL соединение установлено (OK) {db_manager.connection_string}")
    except Exception as e:
        logger.critical(
            f"Lifespan: ОШИБКА ПОДКЛЮЧЕНИЯ К БД: {e}, {db_manager.connection_string=}"
        )  # Если БД не отвечает, часто нет смысла запускать приложение  # raise e
    await init_db_extensions()
    logger.success("расширения Postgresql установлены")
    app.state.pg_engine = db_manager.engine

    # create_and_mount_admin(app, DatabaseManager.engine)
    # logger.info("✅ асинхронный двигатель присоединен к админпанели")

    # await MongoDBManager.connect()  # Подключаем Mongo
    # logger.success("Lifespan: соединение с MongoDB установлены")

    # CLICKHOUSE MANAGER INITIATE
    ch_manager = ClickHouseManager()
    await ch_manager.connect()
    app.state.ch_manager = ch_manager
    app.state.ch_client = ch_manager.client
    app.state.ch_repo_factory = ClickHouseRepositoryFactory(ch_manager.client)
    app.state.seaweed_fids_default = await get_dump(app.state.ch_client)
    logger.success(f'заглушка для изображний инициализирована {app.state.seaweed_fids_default}')
    logger.success("✅ ClickHouse connected")

    # SEAWEED
    await init_seaweed(master_url="http://seaweedfs_master:9333")
    logger.success('✅ Seaweed connected with url "http://seaweedfs_master:9333"')

    # VLLM SERVICE MANAGER
    service_manager = ServiceManager(idle_timeout_minutes=10)
    await service_manager.start()
    app.state.service_manager = service_manager
    service_manager.register("translation", TranslationService)
    logger.success("✅ VLLM Service manager started")
    # REDIS
    # redis_manager = RedisManager()
    # await redis_manager.connect()
    # await redis_manager.init_lsh_driver()
    # app.state.redis_manager = redis_manager
    logger.success("✅ FastAPI started")
    yield

    # --- SHUTDOWN ---
    # await app.state.http_client.aclose()
    # await stop_background_tasks()
    # listen_task.cancel()
    # try:
    #     await listen_task
    # except asyncio.CancelledError:
    #     pass
    await DatabaseManager.engine.dispose()
    logger.success('DatabaseManager stopped')
    await ch_manager.close()
    logger.success('ChManager stopped')
    await close_seaweed()
    logger.success('Seaweed stopped')
    await service_manager.stop()
    logger.success('ServiceManager stopped')
    # await redis_manager.disconnect()
    logger.success('RedisManager stopped')
    logger.remove(std_id)
    logger.remove(log_id)
    await logger.complete()
    print('logger closed')

app = FastAPI(title="Hybrid PostgreSQL-Seaweed API",
              lifespan=lifespan,
              swagger_ui_parameters={
                  "docExpansion": "none",  # Сворачивает всё: и теги, и операции
                  "deepLinking": True,  # Позволяет копировать ссылки на конкретные методы
                  "filter": True  # Полезный бонус: добавляет строку поиска в Swagger
              }
              )
# middleware убирает префикс bearer из ответа если он попал туба по ощибке
# app.add_middleware(FixAmisCookieMiddleware)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = perf_counter()

    # Логируем начало запроса {потом убрать из prod - bootleneck}
    logger.info(f"Начало запроса: {request.method} {request.url.path}")

    response = await call_next(request)

    process_time = (perf_counter() - start_time) * 1000
    formatted_process_time = "{0:.2f}".format(process_time)

    # Логируем завершение и время выполнения
    logger.info(
        f"Завершено: {request.method} {request.url.path} | Статус: {response.status_code} | "
        f"Время: {formatted_process_time}мс"
    )

    return response


@app.exception_handler(AppBaseException)
async def app_exception_handler(request: Request, exc: AppBaseException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://abc8888.ru",
        "http://localhost:5173",
        "https://test.abc8888.ru"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")
app.add_middleware(GZipMiddleware, minimum_size=1000)  # минимальный размер для сжатия

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY
)

setup_starlette_admin(app, db_manager.engine)

app.include_router(ApiRouter().router)
app.include_router(GemmaRouter().router)
app.include_router(LwinRouter().router)
app.include_router(PromptRouter().router)
app.include_router(ProptionRouter().router)
app.include_router(WriterRuleRouter().router)
# app.include_router(OllamaRouter().router)
app.include_router(VllmRouter().router)

app.include_router(SeaweedsRouter().router)
# app.include_router(MongoRouter)
app.include_router(HandbookRouter().router)
app.include_router(HandbookRouterPage().router)
app.include_router(CreateRouter().router)
app.include_router(GetRouter().router)
app.include_router(ReadRouter().router)
app.include_router(DeleteRouter().router)
app.include_router(PatchRouter().router)
app.include_router(ItemImageRouter().router)
app.include_router(ItemViewRouter().router)
app.include_router(ItemRouter().router)
app.include_router(DrinkRouter().router)
app.include_router(ISOLanguageRouter().router)
app.include_router(ProducerTitleRouter().router)
app.include_router(ProducerRouter().router)
app.include_router(VintageConfigRouter().router)
app.include_router(DesignationRouter().router)
app.include_router(ClassificationRouter().router)
app.include_router(ParcelRouter().router)
app.include_router(SiteRouter().router)
app.include_router(CategoryRouter().router)
app.include_router(SubcategoryRouter().router)
app.include_router(CountryRouter().router)
app.include_router(RegionRouter().router)
app.include_router(SubregionRouter().router)
app.include_router(SweetnessRouter().router)
app.include_router(FoodRouter().router)
app.include_router(SuperfoodRouter().router)
app.include_router(VarietalRouter().router)
app.include_router(SourceRouter().router)
app.include_router(StatusRouter().router)
app.include_router(CodeRouter().router)
app.include_router(NameRouter().router)
app.include_router(ImageRouter().router)
app.include_router(RawdataRouter().router)
app.include_router(RegistryRouter().router)
app.include_router(OrchestratorRouter().router)
app.include_router(MergingRouter().router)
app.include_router(ClickImportRouter().router)
app.include_router(BaseIngredientRouter().router)
app.include_router(BodyRouter().router)
app.include_router(GlasswareRouter().router)
app.include_router(ScaleRouter().router)
app.include_router(TastingNoteRouter().router)
app.include_router(TranslateRawDataRouter().router)
app.include_router(TranslateHelperRouter().router)
# app.include_router(CustomerRouter().router)
# app.include_router(WarehouseRouter().router)

# app.include_router(ArqWorkerRouter)
app.include_router(auth_router)
app.include_router(user_router)


@app.get("/")
async def read_root():
    return {"message": "Hybrid PostgreSQL (auth) + MongoDB (files) API"}

# auth_site.mount_app(app)

"""
@app.get("/health")
async def health_check(mongo_db: AsyncIOMotorDatabase = Depends(get_mongodb)):
    status_info = {"status": "mongodb healthy",
                   "mongo_connected": mongo_db is not None,
                   "mongo_operational": False}

    if mongo_db is not None:
        try:
            await mongo_db.command('ping')
            status_info["mongo_operational"] = True
        except Exception:
            status_info["status"] = "degraded"

    return status_info
"""

# app/main.py
from fastapi import FastAPI, Request, status
import asyncio
from fastapi.middleware.cors import CORSMiddleware
# from sqladmin import Admin
# from app.middleware.auth_middleware import AuthMiddleware
# from app.admin import sqladm
from fastapi.responses import JSONResponse
# from sqlalchemy.exc import SQLAlchemyError
import logging
from app.core.routers.base import SQLAlchemyError, NotFoundException, ValidationException, ConflictException
from app.core.config.database.db_async import engine, get_db  # noqa: F401
from app.auth.routers import user_router, auth_router
# -------ИМПОРТ РОУТЕРОВ----------
from app.support.category.router import CategoryRouter
from app.support.drink.router import DrinkRouter
from app.support.country.router import CountryRouter
from app.support.customer.router import CustomerRouter
from app.support.warehouse.router import WarehouseRouter
from app.support.food.router import FoodRouter
from app.support.item.router import ItemRouter
from app.support.region.router import RegionRouter
from app.support.color.router import ColorRouter
from app.support.sweetness.router import SweetnessRouter
from app.support.subregion.router import SubregionRouter
from app.support.varietal.router import VarietalRouter
from app.support.type.router import TypeRouter
# from app.core.routers.image_router import router as image_router
# from app.core.security import get_current_active_user

# from app.admin.auth import authentication_backend


logging.basicConfig(level=logging.WARNING)  # в начале main.py или conftest.py

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.add_middleware(AuthMiddleware)


# Глобальный обработчик для кастомных исключений
@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request: Request, exc: NotFoundException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(ConflictException)
async def conflict_exception_handler(request: Request, exc: ConflictException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


# Обработчик для SQLAlchemy ошибок
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database error occurred"},
    )


# Общий обработчик для всех исключений
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


"""authentication_backend = authentication_backend
admin = Admin(
    app=app,
    engine=engine,
    authentication_backend=authentication_backend,
    templates_dir="/app/templates"
)
# --------------подключение админ панели------------------
admin.add_view(sqladm.CategoryAdmin)
admin.add_view(sqladm.DrinkAdmin)
admin.add_view(sqladm.CountryAdmin)
admin.add_view(sqladm.CustomerAdmin)
admin.add_view(sqladm.WarehouseAdmin)
admin.add_view(sqladm.FoodAdmin)
admin.add_view(sqladm.ItemAdmin)
admin.add_view(sqladm.RegionAdmin)
admin.add_view(sqladm.ColorAdmin)
admin.add_view(sqladm.SweetnessAdmin)
admin.add_view(sqladm.SubregionAdmin)
"""


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/wait")
async def wait_some_time(seconds: float):
    await asyncio.sleep(seconds)  # Не блокирует поток
    return {"waited": seconds}

# app.include_router(image_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(CategoryRouter().router)
app.include_router(ColorRouter().router)
app.include_router(CountryRouter().router)
app.include_router(CustomerRouter().router)
app.include_router(FoodRouter().router)
app.include_router(SweetnessRouter().router)
app.include_router(VarietalRouter().router)
app.include_router(RegionRouter().router)
app.include_router(SubregionRouter().router)
app.include_router(WarehouseRouter().router)
app.include_router(DrinkRouter().router)  # ← очень важно
app.include_router(ItemRouter().router)
app.include_router(TypeRouter().router)
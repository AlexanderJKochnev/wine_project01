# app/main.py
from fastapi import FastAPI, Request, status
import asyncio
from fastapi.middleware.cors import CORSMiddleware
# from sqladmin import Admin
# from app.middleware.auth_middleware import AuthMiddleware
# from app.admin import sqladm
from fastapi.responses import JSONResponse
# from sqlalchemy.exc import SQLAlchemyError

from app.core.routers.base import SQLAlchemyError, NotFoundException, ValidationException, ConflictException
from app.core.config.database.db_async import engine, get_db  # noqa: F401
from app.auth.routers import user_router, auth_router
# -------ИМПОРТ РОУТЕРОВ----------
from app.support.category.router import router as category_router
from app.support.drink.router import router as drink_router
from app.support.country.router import router as country_router
from app.support.customer.router import router as customer_router
from app.support.warehouse.router import router as warehouse_router
from app.support.food.router import router as food_router
from app.support.item.router import router as item_router
from app.support.region.router import router as region_router
from app.support.color.router import router as color_router
from app.support.sweetness.router import router as sweetness_router
from app.support.subregion.router import router as subregion_router
# from app.core.routers.image_router import router as image_router
# from app.core.security import get_current_active_user

from app.admin.auth import authentication_backend

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

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(drink_router)
app.include_router(category_router)
app.include_router(country_router)
app.include_router(customer_router)
app.include_router(warehouse_router)
app.include_router(food_router)
app.include_router(item_router)
app.include_router(region_router)
app.include_router(color_router)
app.include_router(sweetness_router)
app.include_router(subregion_router)
# app.include_router(image_router)

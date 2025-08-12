# app/main.py
from fastapi import FastAPI
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin
from app.admin import sqladm
from app.core.config.database.db_noclass import engine
from app.support.category.listeners import *  # noqa F403
# -------ИМПОРТ РОУТЕРОВ----------
from app.support.category.router import router as category_router
from app.support.drink.router import router as drink_router
from app.support.country.router import router as country_router
from app.support.customer.router import router as customer_router
from app.support.warehouse.router import router as warehouse_router
from app.support.food.router import router as food_router
from app.support.item.router import router as item_router
from app.support.region.router import router as region_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def authenticate(username: str, password: str):
    if username == "admin" and password == "password":
        return True
    return False

admin = Admin(app, engine)

# --------------подключение админ панели------------------
admin.add_view(sqladm.CategoryAdmin)
admin.add_view(sqladm.DrinkAdmin)
admin.add_view(sqladm.CountryAdmin)
admin.add_view(sqladm.CustomerAdmin)
admin.add_view(sqladm.WarehouseAdmin)
admin.add_view(sqladm.FoodAdmin)
admin.add_view(sqladm.ItemAdmin)
admin.add_view(sqladm.RegionAdmin)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/wait")
async def wait_some_time(seconds: float):
    await asyncio.sleep(seconds)  # Не блокирует поток
    return {"waited": seconds}

# --------------подключение роутеров---------------
app.include_router(drink_router)
app.include_router(category_router)
app.include_router(country_router)
app.include_router(customer_router)
app.include_router(warehouse_router)
app.include_router(food_router)
app.include_router(item_router)
app.include_router(region_router)

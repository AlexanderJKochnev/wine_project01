# app/main.py
from fastapi import FastAPI
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin
# from app.middleware.auth_middleware import AuthMiddleware
from app.admin import sqladm
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
from app.core.routers.image_router import router as image_router
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

"""
async def authenticate(username: str, password: str):
    if username == "admin" and password == "password":
        return True
    return False
"""

admin = Admin(
    app,
    engine,
    authentication_backend=authentication_backend,
    templates_dir="templates"
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


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/wait")
async def wait_some_time(seconds: float):
    await asyncio.sleep(seconds)  # Не блокирует поток
    return {"waited": seconds}

# --------подлкючение защищенных роутеров ----------
"""
protected_routers = [
    drink_router,
    category_router,
    country_router,
    customer_router,
    warehouse_router,
    food_router,
    item_router,
    region_router,
    color_router,
    sweetness_router,
    image_router]

for router in protected_routers:
    app.include_router(router, dependencies=[Depends(get_current_active_user)])
"""
# --------подключение незащищенных роутеров ---------
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
app.include_router(image_router)

from tests.utility.data_generators import FieldsData

print('-----------------------------')
# x = prepare_test_cases(app)
# x = get_request_models_from_routes(app)
y = FieldsData(app)
print('-----------------------')

x = y()
if isinstance(x, dict):
    for key, val in x.items():
        print(f'{key} = {val}')
else:
    for key in x:
        print(f'=={key}')
# print_test_cases(app)

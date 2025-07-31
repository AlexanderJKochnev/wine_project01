# app/main.py
from fastapi import FastAPI
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from app.support.users.router import router as user_router
from app.support.category.router import router as category_router
from app.support.drink.router import router as drink_router
from sqladmin import Admin
from app.core.config.database.db_noclass import engine
from app.admin import sqladm


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

"""admin = Admin(
    app,
    engine,
    authentication_backend=authenticate,  # упрощённый пример
    login_view="/admin/login"
)"""


admin = Admin(app, engine)
admin.add_view(sqladm.CategoryAdmin)
admin.add_view(sqladm.DrinkAdmin)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/wait")
async def wait_some_time(seconds: float):
    await asyncio.sleep(seconds)  # Не блокирует поток
    return {"waited": seconds}


app.include_router(drink_router)
app.include_router(category_router)
app.include_router(user_router)

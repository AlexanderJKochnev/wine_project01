# app/auth/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config.database.db_async import get_db
from app.auth.repository import UserRepository
from app.auth.schemas import Token, UserCreate, UserRead
from app.auth.utils import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.auth.dependencies import get_current_active_user
from datetime import timedelta
from app.auth.models import User
# from typing import List

router = APIRouter(prefix="/auth", tags=["auth"])

user_repo = UserRepository()


@router.post("/login", response_model=Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_db)):
    user = await user_repo.authenticate(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}, )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserRead)
async def register_user(user: UserCreate, session: AsyncSession = Depends(get_db)):
    # Проверяем, существует ли пользователь с таким именем
    existing_user = await user_repo.get_by_field("username", user.username, session)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Username already registered")

    # Создаем нового пользователя
    db_user = await user_repo.create(user.model_dump(), session)
    return db_user


@router.get("/users/me", response_model=UserRead)
async def read_users_me(current_user: UserRead = Depends(get_current_active_user)):
    return current_user


@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_active_user)):
    return {"message": f"Hello {current_user.username}"}

# Добавляем метод в репозиторий для получения по полю
# Добавьте в app/core/repositories/sqlalchemy_repository.py метод:
"""
async def get_by_field(self, field_name: str, field_value: Any, session: AsyncSession):
    stmt = select(self.model).where(getattr(self.model, field_name) == field_value)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
"""

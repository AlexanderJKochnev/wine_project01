# app/auth/routers/user.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config.database.db_async import get_db
from app.auth.repository import UserRepository
from app.auth.schemas import UserCreate, UserRead, UserResponse, UserUpdate
from app.auth.dependencies import get_current_active_user
from app.auth.models import User

router = APIRouter(prefix="/users", tags=["users"])

user_repo = UserRepository()


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, session: AsyncSession = Depends(get_db)):
    # Проверяем, существует ли пользователь с таким именем
    existing_user = await user_repo.get_by_field("username", user.username, session)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Username already registered")

    # Создаем нового пользователя
    db_user = await user_repo.create(user.model_dump(), session)
    return db_user


@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: UserRead = Depends(get_current_active_user)):
    return current_user


@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_active_user)):
    return {"message": f"Hello {current_user.username}"}


@router.get("/{id}", response_model=UserResponse)
async def read_user(id: int, db: AsyncSession = Depends(get_db),
                    current_user: User = Depends(get_current_active_user)):
    """Получение пользователя по ID"""
    user = await user_repo.get_by_id(user_id=id, session=db)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{id}", response_model=UserResponse)
async def update_user(
    id: int, user_update: UserUpdate, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Обновление пользователя"""
    if current_user.id != id and current_user.disabled:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    db_user = await user_repo.update(id, user_update, db)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

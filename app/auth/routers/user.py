# app/auth/routers/user.py
from typing import List
from fastapi import APIRouter, Depends, Form, HTTPException, status, BackgroundTasks
from pydantic import EmailStr, SecretStr
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config.database.db_async import get_db
from app.core.schemas.base import DeleteResponse
from app.auth.repository import UserRepository
from app.auth.service import UserService
from app.auth.schemas import UserCreate, UserRead, UserResponse, UserUpdate
from app.auth.dependencies import get_current_active_user
from app.auth.models import User
from app.core.config.project_config import settings

prefix = settings.USER_PREFIX
router = APIRouter(prefix=f"/{prefix}", tags=[f"{prefix}"])

repository = UserRepository
service = UserService
model = User


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, session: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    #   Создание нового пользователя с проверкой, существует ли пользователь с таким именем
    try:
        db_user, exist = await service.get_or_create(user, repository, model, session, default=('username',))
        if not exist:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered"
            )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'register user.error: {e}')
    return db_user


@router.post("/create", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(username: str = Form(..., description='имя пользователя'),
                      password: SecretStr = Form(..., description='пароль'),
                      email: EmailStr | None = Form(..., description='e-mail'),
                      is_active: bool = Form(True, description='активный пользоветель'),
                      is_superuser: bool = Form(False, description='супервользователь'),
                      session: AsyncSession = Depends(get_db), current_user: User = Depends(
                      get_current_active_user)):
    #   Создание нового пользователя с проверкой, существует ли пользователь с таким именем
    try:
        user = UserCreate(username=username, password=password, email=email, is_active=is_active,
                          is_superuser=is_superuser)
        db_user, exist = await service.get_or_create(user, repository, model, session, default=('username',))
        if not exist:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered"
            )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'register user.error: {e}')
    return db_user


@router.patch("/change_password", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def change_password(background_task: BackgroundTasks,
                          user: str = Form(..., description='пользователь'),
                          current_password: SecretStr = Form(..., description='текущий пароль'),
                          new_password: SecretStr = Form(..., description='новый пароль'),
                          repeat_password: SecretStr = Form(..., description='повтори новый пароль'),
                          session: AsyncSession = Depends(get_db),
                          current_user: User = Depends(get_current_active_user)):
    """
        смена пароля
        в случае ошибки подсказки не выдает
    """
    # пои
    detail = 'User not found or password is incorrect or new password is the same as surrent one'
    try:
        response = await service.change_password(user, current_password, new_password, repeat_password, User,
                                                 repository, session)
        return response
    except Exception:
        raise HTTPException(status_code=500, detail=detail)


@router.get("/get_full", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
async def get_users(session: AsyncSession = Depends(get_db),
                    current_user: User = Depends(get_current_active_user)):
    """ получениее списка пользователей """
    result = await service.get_full(repository, model, session)
    return result


@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: UserRead = Depends(get_current_active_user)):
    """ получить данные о себе """
    return current_user


@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_active_user)):
    """ проверка отклика """
    return {"message": f"Hello {current_user.username}"}


@router.get("/{id}", response_model=UserResponse)
async def read_user(id: int, db: AsyncSession = Depends(get_db),
                    current_user: User = Depends(get_current_active_user)):
    """Получение пользователя по ID"""
    user = await repository.get_by_id(id=id, model=User, session=db)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{id}", response_model=UserResponse)
async def update_user(
    id: int, user_update: UserUpdate, background_task: BackgroundTasks, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """ Обновление данных пользователя """
    if current_user.id != id and current_user.is_superuser is False:
        # только super или сам пользователь менять свои данные
        raise HTTPException(status_code=403, detail="Not enough permissions")

    result: dict = await service.patch(id, user_update, repository, model, background_task, db)
    user: User = result.get('data')
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # user_dict = user.to_dict()
    # return UserResponse(**user_dict)
    return UserResponse(**user)


@router.delete("/{id}", response_model=DeleteResponse)
async def delete_user(id: int, background_task: BackgroundTasks, db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_active_user)):
    try:
        result = await service.delete(id, model, repository, background_task, db)
        print(f'{result=} f{type(result)=}')
    except Exception as e:
        raise HTTPException(status_code=501, detail=e)

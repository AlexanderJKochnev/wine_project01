# app/auth/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config.database.db_async import get_db
from app.auth.repository import UserRepository
from app.auth.utils import verify_token
from app.auth.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

user_repo = UserRepository()


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}, )
    token_data = verify_token(token, credentials_exception)

    user = await user_repo.get_by_field("username", token_data.username, session)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
        current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_active_superuser(
        current_user: User = Depends(get_current_active_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=400,
                            detail="The user doesn't have enough privileges")
    return current_user

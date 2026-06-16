# app/auth/schemas.py
from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field
from typing import Optional
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: str
    email: Optional[EmailStr] = None
    is_active: bool = True
    is_superuser: bool = False


class UserFree(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: Optional[str]
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False


class UserCreate(UserBase):
    password: str


class UserUpdate(UserFree):
    password: Optional[str] = None


class UserRead(UserBase):
    id: int


class UserInDB(UserFree):
    password: Optional[str] = Field(default=None, exclude=True)

    @computed_field(return_type=str)
    @property
    def hashed_password(self) -> str:
        if self.password:
            return pwd_context.hash(self.password)
        return None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

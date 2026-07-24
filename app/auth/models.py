# app/auth/models.py
from datetime import datetime

from sqlalchemy import DateTime, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.core.models.base_model import Base
from typing import Optional
from fastapi_user_auth.auth.models import Role as ARole, CasbinRule as ACasbinRule, LoginHistory as ALoginHistory


class Role(Base, ARole):
    __tablename__ = "auth_role"
    pass


class CasbinRule(Base, ACasbinRule):
    __tablename__ = "auth_casbin_rule"
    pass


class LoginHistory(Base, ALoginHistory):
    __tablename__ = "auth_login_history"
    pass


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    delete_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=None)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

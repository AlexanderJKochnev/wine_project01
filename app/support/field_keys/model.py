# app/support/field_keys/model.py
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.core.models.base_model import Base, BaseAt


class FieldKey(Base, BaseAt):
    __tablename__ = 'field_keys'
    
    short_name: Mapped[str] = mapped_column(String(25), index=True)  # краткое имя до 25 знаков
    full_name: Mapped[str] = mapped_column(String(500), unique=True, index=True)  # полное имя ключа
    frequency: Mapped[int] = mapped_column(Integer, default=0)  # частота встречания
    
    def __str__(self):
        return self.short_name or self.full_name or ""
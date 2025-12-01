# app/support/field_keys/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FieldKeyBase(BaseModel):
    short_name: str
    full_name: str
    frequency: int = 0


class FieldKeyCreate(FieldKeyBase):
    short_name: str
    full_name: str


class FieldKeyUpdate(BaseModel):
    short_name: Optional[str] = None
    full_name: Optional[str] = None


class FieldKeyResponse(FieldKeyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
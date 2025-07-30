# app/core/schemas/base_schema.py

""" Base Pydantic Model """
from typing import NewType
from pydantic import BaseModel

PyModel = NewType("PyModel", BaseModel)


class Base(BaseModel):
    class Config:
        from_attributes = True

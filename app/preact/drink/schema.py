# app/preact/drink/schema.py
"""
    Create
    Read
    Delete
    Update
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import Field, model_validator, computed_field
from app.core.utils.common_utils import camel_to_enum
from app.core.schemas.image_mixin import ImageUrlMixin
from app.core.schemas.base import BaseModel, CreateResponse
from app.support.drink.schemas import DrinkCreateRelation, DrinkReadApi, DrinkReadFlat

# app/core/models/mongo_mixin.py
from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_mixin
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class MongoRef(BaseModel):
    mongo_id: Optional[PyObjectId] = Field(alias="_id")
    filename: str
    content_type: str
    url: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        populate_by_name = True


@declarative_mixin
class MongoMixin:
    """Mixin для добавления ссылки на документ в MongoDB"""

    mongo_ref_id = Column(String(100), nullable=True, index=True, doc="ID документа в MongoDB")

    def set_mongo_ref(self, mongo_id: str):
        self.mongo_ref_id = mongo_id

    @property
    def has_mongo_document(self) -> bool:
        return self.mongo_ref_id is not None

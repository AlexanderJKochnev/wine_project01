# app/support/sweetness/schemas.py

from app.core.schemas.base import (CreateSchema, ReadSchema, UpdateSchema, CreateResponse)


class CustomReadSchema:
    pass


class CustomCreateSchema:
    pass


class CustomCreateRelation:
    pass


class CustomUpdSchema:
    pass


class SweetnessRead(ReadSchema, CustomReadSchema):
    pass


class SweetnessReadRelation(SweetnessRead):
    pass


class SweetnessCreateRelation(CreateSchema, CustomCreateRelation):
    pass


class SweetnessCreate(CreateSchema, CustomCreateSchema):
    pass


class SweetnessUpdate(UpdateSchema, CustomUpdSchema):
    pass


class SweetnessCreateResponseSchema(SweetnessCreate, CreateResponse):
    pass

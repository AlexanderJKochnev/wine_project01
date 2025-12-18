# app/support/varietal/schemas.py
from app.core.schemas.base import (CreateSchema, ReadSchema, UpdateSchema,
                                   CreateResponse, PkSchema)


class CustomReadSchema:
    pass


class CustomCreateSchema:
    pass


class CustomCreateRelation:
    pass


class CustomUpdSchema:
    pass


class VarietalRead(ReadSchema, CustomReadSchema):
    pass


class VarietalReadRelation(VarietalRead):
    pass


class VarietalCreateRelation(CreateSchema, CustomCreateRelation):
    pass


class VarietalCreate(CreateSchema, CustomCreateSchema):
    pass


class VarietalUpdate(UpdateSchema, CustomUpdSchema):
    pass


class VarietalCreateResponseSchema(VarietalCreate, CreateResponse):
    pass


class VarietalId(PkSchema):
    pass
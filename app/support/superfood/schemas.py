# app/support/superfood/schemas.py

from app.core.schemas.base import CreateSchema, ReadSchema, UpdateSchema, CreateResponse


class CustomReadSchema:
    pass


class CustomCreateSchema:
    pass


class CustomCreateRelation:
    pass


class CustomUpdSchema:
    pass


class SuperfoodRead(ReadSchema, CustomReadSchema):
    pass


class SuperfoodReadRelation(ReadSchema, CustomCreateRelation):
    pass


class SuperfoodCreateRelation(CreateSchema, CustomCreateRelation):
    pass


class SuperfoodCreate(CreateSchema, CustomCreateSchema):
    pass


class SuperfoodUpdate(UpdateSchema, CustomUpdSchema):
    pass


class SuperfoodCreateResponseSchema(SuperfoodCreate, CreateResponse):
    pass

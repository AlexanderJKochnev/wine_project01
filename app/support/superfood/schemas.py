# app/support/superfood/schemas.py

from pydantic import ConfigDict

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
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)


class SuperfoodCreateRelation(CreateSchema, CustomCreateRelation):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)


class SuperfoodCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)


class SuperfoodUpdate(UpdateSchema, CustomUpdSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)


class SuperfoodCreateResponseSchema(SuperfoodCreate, CreateResponse):
    pass

# app/support/country/schemas.py

from app.core.schemas.base import (CreateSchema, ReadSchema, UpdateSchema, CreateResponse)


class CustomReadSchema:
    pass


class CustomCreateSchema:
    pass


class CustomCreateRelation:
    pass


class CustomUpdSchema:
    pass


class CountryRead(ReadSchema, CustomReadSchema):
    pass


class CountryCreateRelation(CreateSchema, CustomCreateRelation):
    pass


class CountryCreate(CreateSchema, CustomCreateSchema):
    pass


class CountryUpdate(UpdateSchema, CustomUpdSchema):
    pass


class CountryCreateResponseSchema(CountryCreate, CreateResponse):
    pass

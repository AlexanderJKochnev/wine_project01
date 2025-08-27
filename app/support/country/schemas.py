# app/support/country/schemas.py


from pydantic import ConfigDict

from app.core.schemas.base import CreateSchema, FullSchema, PkSchema, ReadSchema, ShortSchema, UpdateSchema


class CountryPk(PkSchema):
    pass
    

class CustomSchema:
    pass


class CustomCreateSchema:
    pass


class CustomUpdSchema:
    pass


class CountryShort(ShortSchema):
    pass


class CountryRead(ReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class CountryCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class CountryUpdate(UpdateSchema, CustomUpdSchema):
    pass


class CountryFull(FullSchema, CustomSchema):
    pass

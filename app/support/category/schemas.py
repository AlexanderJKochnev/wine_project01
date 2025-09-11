# app/support/category/schemas.py

from pydantic import ConfigDict

from app.core.schemas.base import CreateSchema, FullSchema, ReadSchema, UpdateSchema


class CustomReadSchema:
    """ кастомные поля """
    pass


class CustomCreateSchema:
    pass


class CustomCreateRelation:
    # сюда добавлять поля если появятся связи см Subregion для примера
    pass


class CustomUpdSchema:
    pass


class CategoryRead(ReadSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class CategoryCreateRelation(CreateSchema, CustomCreateRelation):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)

class CategoryCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class CategoryUpdate(UpdateSchema, CustomUpdSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class CategoryFull(FullSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)

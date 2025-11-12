# app/support/category/schemas.py

from app.core.schemas.base import CreateSchema, ReadSchema, UpdateSchema, CreateResponse, DetailView


class CustomReadSchema:
    pass


class CustomCreateSchema:
    pass


class CustomCreateRelation:
    pass


class CustomUpdSchema:
    pass


class CategoryRead(ReadSchema, CustomReadSchema):
    pass


class CategoryReadRelation(ReadSchema, CustomReadSchema):
    pass


class CategoryCreateRelation(CreateSchema, CustomCreateRelation):
    pass


class CategoryCreate(CreateSchema, CustomCreateSchema):
    pass


class CategoryUpdate(UpdateSchema, CustomUpdSchema):
    pass


class CategoryCreateResponseSchema(CategoryCreate, CreateResponse):
    pass


class CategoryDetailView(DetailView):
    pass

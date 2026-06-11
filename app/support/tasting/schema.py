# app/support/category/schemas.py

from app.core.schemas.base import CreateSchema, ReadSchema, UpdateSchema, CreateResponse, DetailView

"""
TastingNote
BaseIngredient
Glassware
Scale
Body
"""


class CustomReadSchema:
    pass


class CustomCreateSchema:
    pass


class CustomCreateRelation:
    pass


class CustomUpdSchema:
    pass


class TastingNoteRead(ReadSchema, CustomReadSchema):
    pass


class TastingNoteReadRelation(ReadSchema, CustomReadSchema):
    pass


class TastingNoteCreateRelation(CreateSchema, CustomCreateRelation):
    pass


class TastingNoteCreate(CreateSchema, CustomCreateSchema):
    pass


class TastingNoteUpdate(UpdateSchema, CustomUpdSchema):
    pass


class TastingNoteCreateResponseSchema(TastingNoteCreate, CreateResponse):
    pass


class TastingNoteDetailView(DetailView):
    pass


class BaseIngredientRead(ReadSchema, CustomReadSchema):
    pass


class BaseIngredientReadRelation(ReadSchema, CustomReadSchema):
    pass


class BaseIngredientCreateRelation(CreateSchema, CustomCreateRelation):
    pass


class BaseIngredientCreate(CreateSchema, CustomCreateSchema):
    pass


class BaseIngredientUpdate(UpdateSchema, CustomUpdSchema):
    pass


class BaseIngredientCreateResponseSchema(BaseIngredientCreate, CreateResponse):
    pass


class BaseIngredientDetailView(DetailView):
    pass

# ---------
class GlasswareRead(ReadSchema, CustomReadSchema):
    pass


class GlasswareReadRelation(ReadSchema, CustomReadSchema):
    pass


class GlasswareCreateRelation(CreateSchema, CustomCreateRelation):
    pass


class GlasswareCreate(CreateSchema, CustomCreateSchema):
    pass


class GlasswareUpdate(UpdateSchema, CustomUpdSchema):
    pass


class GlasswareCreateResponseSchema(GlasswareCreate, CreateResponse):
    pass


class GlasswareDetailView(DetailView):
    pass


class ScaleRead(ReadSchema, CustomReadSchema):
    pass


class ScaleReadRelation(ReadSchema, CustomReadSchema):
    pass


class ScaleCreateRelation(CreateSchema, CustomCreateRelation):
    pass


class ScaleCreate(CreateSchema, CustomCreateSchema):
    pass


class ScaleUpdate(UpdateSchema, CustomUpdSchema):
    pass


class ScaleCreateResponseSchema(ScaleCreate, CreateResponse):
    pass


class ScaleDetailView(DetailView):
    pass


class BodyRead(ReadSchema, CustomReadSchema):
    pass


class BodyReadRelation(ReadSchema, CustomReadSchema):
    pass


class BodyCreateRelation(CreateSchema, CustomCreateRelation):
    pass


class BodyCreate(CreateSchema, CustomCreateSchema):
    pass


class BodyUpdate(UpdateSchema, CustomUpdSchema):
    pass


class BodyCreateResponseSchema(BodyCreate, CreateResponse):
    pass


class BodyDetailView(DetailView):
    pass
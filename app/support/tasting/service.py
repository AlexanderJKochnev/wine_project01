# app.support.tasting.service.py
from app.core.services.service import Service
from app.support.tasting.repository import (BaseIngredientRepository, BodyRepository, GlasswareRepository,
                                            ScaleRepository, TastingNoteRepository)


class BaseIngredientService(Service):
    pass


class BodyService(Service):
    pass


class GlasswareService(Service):
    pass


class ScaleService(Service):
    pass


class TastingNoteService(Service):
    pass

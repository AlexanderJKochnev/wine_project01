# app/support/tasting/repository.py

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.repositories.sqlalchemy_repository import HandbookRepository
from app.core.types import ModelType
from app.support import BaseIngredient, Body, Glassware, Scale, TastingNote
from app.support.drink.model import Drink, DrinkBaseIngredient, DrinkTastingNote
from app.support.item.model import Item


# CategoryRepository = RepositoryFactory.get_repository(Category)
# class CategoryRepository(Repository):
#    model = Category


class BaseIngredientRepository(HandbookRepository):
    model = BaseIngredient

    @classmethod
    def get_item_drink(cls, id: int):
        return select(Item.id, Item.drink_id).where(
            Drink.id == Item.drink_id, Drink.id == DrinkBaseIngredient.drink_id,
            DrinkBaseIngredient.baseingredient_id == id
        )

    @classmethod
    def get_query(cls, model: ModelType):
        # Добавляем загрузку связи с relationships
        return select(BaseIngredient).options(selectinload(BaseIngredient.drink_associations)
                                              .joinedload(DrinkBaseIngredient.drink))


class TastingNoteRepository(HandbookRepository):
    model = TastingNote

    @classmethod
    def get_item_drink(cls, id: int):
        return select(Item.id, Item.drink_id).where(
            Drink.id == Item.drink_id, Drink.id == DrinkTastingNote.drink_id,
            DrinkTastingNote.tastingnote_id == id
        )

    @classmethod
    def get_query(cls, model: ModelType):
        # Добавляем загрузку связи с relationships
        return select(TastingNote).options(selectinload(TastingNote.drink_associations)
                                           .joinedload(DrinkTastingNote.drink))


class BodyRepository(HandbookRepository):
    model = Body

    @classmethod
    def get_item_drink(cls, id: int):
        return select(Item.id, Item.drink_id).where(
            Drink.id == Item.drink_id,
            Drink.body_id == id)


class GlasswareRepository(HandbookRepository):
    model = Glassware

    @classmethod
    def get_item_drink(cls, id: int):
        return select(Item.id, Item.drink_id).where(
            Drink.id == Item.drink_id,
            Drink.glassware_id == id)


class ScaleRepository(HandbookRepository):
    model = Scale

    @classmethod
    def get_item_drink(cls, id: int):
        return select(Item.id, Item.drink_id).where(
            Drink.id == Item.drink_id,
            Drink.scale_id == id)

# app/support/tasting/router.py

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, BackgroundTasks
from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support import BaseIngredient, Body, Glassware, Scale, TastingNote
from app.support.tasting.schema import BaseIngredientCreate, BaseIngredientCreateRelation, BaseIngredientUpdate, \
    BodyCreate, BodyCreateRelation, BodyUpdate, GlasswareCreate, GlasswareCreateRelation, GlasswareUpdate, ScaleCreate, \
    ScaleCreateRelation, ScaleUpdate, TastingNoteCreate, TastingNoteCreateRelation, TastingNoteUpdate


class BaseIngredientRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=BaseIngredient,
            prefix="/BaseIngredients".lower(),
        )

    async def create(self, data: BaseIngredientCreate,
                     session: AsyncSession = Depends(get_db)):
        return await super().create(data, session)

    async def patch(self, id: int, data: BaseIngredientUpdate, background_tasks: BackgroundTasks,
                    session: AsyncSession = Depends(get_db)):
        return await super().patch(id, data, background_tasks, session)

    async def create_relation(self, data: BaseIngredientCreateRelation,
                              session: AsyncSession = Depends(get_db)):
        result = await super().create_relation(data, session)
        return result


class BodyRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Body,
            prefix="/Bodies".lower(),
        )

    async def create(self, data: BodyCreate,
                     session: AsyncSession = Depends(get_db)):
        return await super().create(data, session)

    async def patch(self, id: int, data: BodyUpdate, background_tasks: BackgroundTasks,
                    session: AsyncSession = Depends(get_db)):
        return await super().patch(id, data, background_tasks, session)

    async def create_relation(self, data: BodyCreateRelation,
                              session: AsyncSession = Depends(get_db)):
        result = await super().create_relation(data, session)
        return result


class GlasswareRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Glassware,
            prefix="/Glasswares".lower(),
        )

    async def create(self, data: GlasswareCreate,
                     session: AsyncSession = Depends(get_db)):
        return await super().create(data, session)

    async def patch(self, id: int, data: GlasswareUpdate, background_tasks: BackgroundTasks,
                    session: AsyncSession = Depends(get_db)):
        return await super().patch(id, data, background_tasks, session)

    async def create_relation(self, data: GlasswareCreateRelation,
                              session: AsyncSession = Depends(get_db)):
        result = await super().create_relation(data, session)
        return result


class ScaleRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Scale,
            prefix="/Scales".lower(),
        )

    async def create(self, data: ScaleCreate,
                     session: AsyncSession = Depends(get_db)):
        return await super().create(data, session)

    async def patch(self, id: int, data: ScaleUpdate, background_tasks: BackgroundTasks,
                    session: AsyncSession = Depends(get_db)):
        return await super().patch(id, data, background_tasks, session)

    async def create_relation(self, data: ScaleCreateRelation,
                              session: AsyncSession = Depends(get_db)):
        result = await super().create_relation(data, session)
        return result


class TastingNoteRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=TastingNote,
            prefix="/TastingNotes".lower(),
        )

    async def create(self, data: TastingNoteCreate,
                     session: AsyncSession = Depends(get_db)):
        return await super().create(data, session)

    async def patch(self, id: int, data: TastingNoteUpdate, background_tasks: BackgroundTasks,
                    session: AsyncSession = Depends(get_db)):
        return await super().patch(id, data, background_tasks, session)

    async def create_relation(self, data: TastingNoteCreateRelation,
                              session: AsyncSession = Depends(get_db)):
        result = await super().create_relation(data, session)
        return result

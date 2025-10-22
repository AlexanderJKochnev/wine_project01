# app/support/subcategory/repository.py

from typing import List, Tuple
from app.support.subcategory.model import Subcategory
from app.support.category.model import Category
from app.core.repositories.sqlalchemy_repository import Repository
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession


class SubcategoryRepository(Repository):
    model = Subcategory

    @classmethod
    async def fetch_name_triples(cls, category_expr: ColumnElement,
                                 subcategory_expr: ColumnElement,
                                 session: AsyncSession) -> List[Tuple[int, str, str]]:
        """
        Возвращает [(subcategory_id, category_name, subcategory_name), ...]
        """
        stmt = (select(
            Subcategory.id,
                category_expr.label("category_name"),
                subcategory_expr.label("subcategory_name"),).join(Category, Subcategory.category_id == Category.id))
        result = await session.execute(stmt)
        return result.all()  # list of tuples
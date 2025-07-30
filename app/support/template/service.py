# app/support/template/service.py

""" Data Access Object  """
from sqlalchemy import select
from app.support.template.models import TemplateModel
from app.core.config.database.db_noclass import async_session_maker


class TemplateDAO:
    @classmethod
    async def find_all_students(cls):
        async with async_session_maker() as session:
            query = select(TemplateModel)
            templates = await session.execute(query)
            return templates.scalars().all()

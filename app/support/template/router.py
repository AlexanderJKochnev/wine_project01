# app/support/template/router.py

from fastapi import APIRouter   # noqa: F401
from app.support.template.service import TemplateDAO
# from sqlalchemy import select   # noqa: F401
# from app.core.config.database.db_helper import db_helper     # noqa: F401
# from app.support.template.models import TemplateModel     # noqa: F401
# from app.core.config.database.db_noclass import async_session_maker


tag1: str = 'template short_notice'
tag2: str = 'template get_notice'
prefix = '/template'
router = APIRouter(prefix=f'{prefix}', tags=[f'{tag1}'])


@router.get("/", summary=tag2)
async def get_all_templates():
    return await TemplateDAO.find_all_students()

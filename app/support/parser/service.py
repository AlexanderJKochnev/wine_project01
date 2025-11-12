# app/support/parser/service.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.services.service import Service
# from app.support.parser.model import Code, Name, Image, Rawdata
# from app.support.parser.repository import CodeRepository, NameRepository, ImageRepository, RawdataRepository
# from app.support.subcategory.schemas import SubcategoryCreate, SubcategoryCreateRelation, SubcategoryRead


class CodeService(Service):
    pass


class NameService(Service):
    pass


class ImageService(Service):
    pass


class RawdataService(Service):
    pass


class StatusService(Service):
    pass

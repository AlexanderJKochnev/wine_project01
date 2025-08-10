# app/support/template/schemas.py
"""
замени Template на имя модели в единственном числе с сохранением регистра
"""
from app.core.schemas.dynamic_schema import create_pydantic_models_from_orm
from app.support.template.models import Template

TemplateSchemas = create_pydantic_models_from_orm(Template)
SAdd = TemplateSchemas['Create']
SUpd = TemplateSchemas['Update']
SDel = TemplateSchemas['DeleteResponse']
SRead = TemplateSchemas['Read']
SList = TemplateSchemas['List']
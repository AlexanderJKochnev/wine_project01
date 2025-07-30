# app/support/template/models.py

""" SQLAlchemy models """
from sqlalchemy import String   # noqa: F401
from sqlalchemy.orm import Mapped, mapped_column    # noqa: F401
from sqlalchemy import ForeignKey   # noqa: F401
from app.core.models import base_model as base


class TemplateModel(base.Base):
    name: Mapped[base.str_uniq]
    description: Mapped[base.str_null_true]

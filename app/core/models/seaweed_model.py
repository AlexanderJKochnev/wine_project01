# app/core/models/seaweed._model.py
"""
    тестовая модель для хранения картинок
"""
from sqlalchemy.orm import Mapped
from app.core.models.base_model import Base, str_null_false


class File(Base):
    filename = Mapped[str_null_false]
    content_type = Mapped[str_null_false]
    # seaweedfs_id = Mapped[str_uniq] # it will be name inherited from Base

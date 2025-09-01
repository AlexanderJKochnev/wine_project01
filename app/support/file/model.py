# app/support/file/model/model.py
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.models.base_model import Base, BaseAt
from app.core.models.mongo_mixin import MongoMixin


class Image(Base, BaseAt, MongoMixin):
    title = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    alt_text = Column(String(300), nullable=True)
    uploaded_by = Column(ForeignKey("users.id"), nullable=True)

    uploader = relationship("User", back_populates="images")


class Document(Base, BaseAt, MongoMixin):
    __tablename__ = "documents"

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    uploaded_by = Column(ForeignKey("users.id"), nullable=True)

    uploader = relationship("User", back_populates="documents")
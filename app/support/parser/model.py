# app/support/parser/model.py
from sqlalchemy import String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List
from app.core.models.base_model import Base, BaseAt
from app.core.models.image_mixin import ImageMixin
from sqlalchemy import ForeignKey, UniqueConstraint


class Code(Base, BaseAt):

    code: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    url: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    status: Mapped["Status"] = relationship("Status", back_populates="codes")
    status_id: Mapped[int] = mapped_column(ForeignKey("status.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    names: Mapped[List["Name"]] = relationship("Name", back_populates="code", cascade="all, delete-orphan")

    def __str__(self):
        return self.code or ""


class Name(Base, BaseAt):

    code_id: Mapped[int] = mapped_column(ForeignKey("codes.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    url: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    status: Mapped["Status"] = relationship("Status", back_populates="names")
    status_id: Mapped[int] = mapped_column(ForeignKey("status.id", ondelete="SET NULL"), nullable=True)

    # Relationships с каскадным удалением
    code: Mapped["Code"] = relationship("Code", back_populates="names")
    raw_data: Mapped[Optional["Rawdata"]] = relationship(
        "Rawdata", back_populates="name", cascade="all, delete-orphan", uselist=False)
    images: Mapped[List["Image"]] = relationship("Image", back_populates="name", cascade="all, delete-orphan")


class Rawdata(Base, BaseAt):

    name_id: Mapped[int] = mapped_column(ForeignKey("names.id", ondelete="CASCADE"), unique=True)
    body_html: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped["Status"] = relationship("Status", back_populates="rawdatas")
    status_id: Mapped[int] = mapped_column(ForeignKey("status.id", ondelete="SET NULL"), nullable=True)

    name: Mapped["Name"] = relationship("Name", back_populates="raw_data")

    def __str__(self):
        return self.name or ""


class Image(Base, BaseAt, ImageMixin):
    __table_args__ = (UniqueConstraint('image_id', 'name_id', name='uq_parser_images_unique'),)
    name_id: Mapped[int] = mapped_column(ForeignKey("names.id", ondelete="CASCADE"))
    name: Mapped["Name"] = relationship("Name", back_populates="images")

    def __str__(self):
        return self.name or ""


class Status(Base, BaseAt):
    status: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    # Relationships
    codes: Mapped[List["Code"]] = relationship("Code", back_populates="status")
    names: Mapped[List["Name"]] = relationship("Name", back_populates="status")
    rawdatas: Mapped[List["Rawdata"]] = relationship("Rawdata", back_populates="status")

    def __str__(self):
        return self.status or ""

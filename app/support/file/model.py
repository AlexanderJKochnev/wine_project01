# app/support/file/model.py
from __future__ import annotations
from sqlalchemy.orm import Mapped
from app.core.models.base_model import Base, str_null_false, str_uniq
from typing import Optional

# if TYPE_CHECKING:


class File(Base):
    content_type: Mapped[str_null_false]
    seaweedfs_id: Mapped[str_uniq]  # it will be name inherited from Base
    filename: Mapped[str_null_false]
    size: Mapped[int]

from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models.base_model import Base, int_pk, str_uniq, str_null_true


class User(Base):
    id: Mapped[int_pk]
    user_name: Mapped[str_uniq]
    phone_number: Mapped[str_null_true]
    first_name: Mapped[str_null_true]
    last_name: Mapped[str_null_true]
    email: Mapped[str_uniq]
    password: Mapped[str]

    is_user: Mapped[bool] = mapped_column(default=True,
                                          server_default=text('true'),
                                          nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False,
                                           server_default=text('false'),
                                           nullable=False)
    is_super_admin: Mapped[bool] = mapped_column(default=False,
                                                 server_default=text('false'),
                                                 nullable=False)

    extend_existing = True

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"

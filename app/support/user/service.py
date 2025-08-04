from app.core.services.base import BaseDAO
from app.support.user.models import User


class UsersDAO(BaseDAO):
    model = User

from app.core.services.base import BaseDAO
from app.support.users.models import User


class UsersDAO(BaseDAO):
    model = User

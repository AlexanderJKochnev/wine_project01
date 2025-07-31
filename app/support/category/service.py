""" Data Access Object  """
from app.support.category.models import Category
from app.core.services.base import BaseDAO


class CategoryDAO(BaseDAO):
    model = Category

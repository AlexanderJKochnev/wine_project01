# django_admin/apps/base/fields.py
from django.db import models


class MongoFileField(models.FileField):
    """
    Поле для хранения ссылки на файл в MongoDB
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 255)
        super().__init__(*args, **kwargs)

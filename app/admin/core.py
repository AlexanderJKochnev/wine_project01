# app.admin.core.py
"""
core component of views
"""
from starlette_admin import IntegerField, StringField, TextAreaField

# FIELDS
id = IntegerField("id", label="ID", exclude_from_create=True)
name = StringField("name", label="Name", required=True, searchable=True, orderable=True)
name_ru = StringField("name_ru", label="Наименование", required=False, searchable=True, orderable=True)
description = TextAreaField("description", label="Description", required=False, exclude_from_list=True)

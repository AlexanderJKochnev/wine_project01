# app.admin.core.py
"""
core component of views
"""
from starlette_admin import DateTimeField, IntegerField, StringField, TextAreaField

from app.core.config.project_config import settings


class FieldsCore():
    """
    заготовки для поле AdminViews
    HasOne(
            "user",                    # Точное имя атрибута relationship с back_populates
            identity="user",           # Идентификатор связанной модели в админке
            label="Пользователь",
        ),
    """
    def __init__(self):
        # локализованные поля ('name', 'description', ...)
        self.fields_localized: tuple = settings.FIELDS_LOCALIZED
        # языковые суффиксы ('', '_ru', ...)
        self.langs: tuple = settings.lang_suffixes
        # поля типа  TextAreaField
        self.textareafields: tuple = ('description',)
        self.id = IntegerField("id", label="ID", exclude_from_create=True)
        self.created_at = DateTimeField("created_at", label="Дата создания", exclude_from_list=True,
                                        exclude_from_create=True, exclude_from_edit=True,
                                        orderable=True)
        self.update_at = DateTimeField(
            "created_at", label="Дата обновления", exclude_from_list=True, exclude_from_create=True,
            exclude_from_edit=True, orderable=True
        )
        self.localized_fields = self.localized_field_generator()

    def localized_field_generator(self) -> list:
        """
            возвращает список локлизованных полей
        """
        strfields: list = []
        textfields: list = []
        for lang in self.langs:
            required = True if lang == '' else False
            for field in self.fields_localized:
                if field in self.textareafields:
                    textfields.append(TextAreaField(field, label=field.capitalize(),
                                                    required=False, exclude_from_list=True))
                else:
                    strfields.append(StringField(field, label=field.capitalize(),
                                                 required=required, searchable=True, orderable=True,
                                                 ))
        result: list = strfields + textfields
        return result

    def __simple__(self):
        self.id = IntegerField("id", label="ID", exclude_from_create=True)

    def __call__(self, *args, **kwargs):
        result: list = [self.id]
        result.extend(self.localized_fields)
        result.append(self.created_at)
        result.append(self.update_at)
        return result
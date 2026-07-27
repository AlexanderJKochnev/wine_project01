# app.admin.core.py
"""
core component of views
"""

from starlette_admin import ColorField, DateTimeField, IntegerField, StringField, TextAreaField

from app.core.config.project_config import settings


class HandBooksFieldsCore():
    """
    заготовки для полей HandBooks AdminViews
    HasOne(
            "user",                    # Точное имя атрибута relationship с back_populates
            identity="user",           # Идентификатор связанной модели в админке
            label="Пользователь",
        ),
    """

    def __init__(self, type: int = 0):
        """
            field
            hasone: список one-to-many fields
        """
        # локализованные поля ('name', 'description', ...)
        print(f'===================={type=}')
        if type == 0:
            self.fields_localized: tuple = settings.handbooks_fields  # settings.FIELDS_LOCALIZED
        elif type == 1:
            self.fields_localized: tuple = settings.drink_fields
        print(f'{self.fields_localized=}')
        # языковые суффиксы ('', '_ru', ...)
        self.langs: tuple = settings.lang_suffixes
        # поля типа  TextAreaField
        self.textareafields: tuple = ('description', 'recomendation')
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
                    textfields.append(TextAreaField(f'{field}{lang}', label=f'{field}{lang}'.capitalize(),
                                                    required=False, exclude_from_list=True))
                else:
                    strfields.append(StringField(f'{field}{lang}', label=f'{field}{lang}'.capitalize(),
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


class CleanColorField(ColorField):
    # 1. Привязываем шаблон для Detail страницы
    display_template = "displays/color.html"
    name = 'color'
    label = 'Цвет'
    help_text = 'Цвет фона на изображении'

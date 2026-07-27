# app.admin.core.py
"""
core component of views
"""
from typing import List, Optional

from starlette.requests import Request
from starlette_admin import ColorField, DateTimeField, HasOne, IntegerField, RequestAction, StringField, TextAreaField

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

    def __init__(self, **kwargs):
        """
            field
            hasone: список one-to-many fields
        """
        self.hasone: Optional[List[HasOne]] = None
        # локализованные поля ('name', 'description', ...)
        self.fields_localized: tuple = settings.handbooks_fields  # settings.FIELDS_LOCALIZED
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
        if hasone := kwargs.get('hasone'):
            print(f'{hasone=} =====')
            self.hasone = [HasOne(item, identity=item) for item in hasone]

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
        if self.hasone:
            result.extend(self.hasone)
        result.extend(self.localized_fields)
        result.append(self.created_at)
        result.append(self.update_at)
        return result


class CleanColorField(ColorField):
    # 1. Привязываем шаблон для Detail страницы
    display_template = "displays/color.html"

    # 2. Указываем ключ JS-функции для List страницы
    render_function_key = "renderColor"

    # 3. Передаем JS-код напрямую через поле, без изменения класса Admin!
    def additional_js_links(self, request: Request, action: RequestAction):
        if action == RequestAction.LIST:
            # Возвращаем инлайн-скрипт в виде data-url, чтобы не создавать файл на диске
            js_code = """
            function renderColor(data, type, row, meta) {
                if (!data) return '';
                return `<div style="display: flex; align-items: center; gap: 8px;">
                            <span style="background-color: ${data}; width: 20px; height: 20px; display: inline-block; border-radius: 4px; border: 1px solid #dee2e6;"></span>
                            <code>${data}</code>
                        </div>`;
            }
            """
            # Кодируем скрипт, чтобы браузер выполнил его на лету
            import base64
            encoded_js = base64.b64encode(js_code.encode('utf-8')).decode('utf-8')
            return [f"data:text/javascript;base64,{encoded_js}"]
        return []

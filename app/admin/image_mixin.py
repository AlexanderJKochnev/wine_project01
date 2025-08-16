# app/admin/image_mixin.py
# from sqladmin import ModelView
from typing import Any
from starlette.requests import Request
# import os


class ImageAdminMixin:
    """Mixin для добавления функционала изображений в админку"""
    # Добавляем изображение в список колонок
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Если модель имеет image_path, добавляем preview
        if hasattr(cls.model, 'image_path'):
            # Добавляем методы для отображения изображений
            if not hasattr(cls, 'column_list') or not cls.column_list:
                # Если column_list не задан, создаем его автоматически
                pass
            else:
                # Если column_list задан как список, добавляем image_preview
                if isinstance(cls.column_list, (list, tuple)):
                    if "image_preview" not in cls.column_list:
                        cls.column_list = list(cls.column_list) + ["image_preview"]

    def get_list_value(self, model: Any, column: Any) -> Any:
        """Отображение превью изображения в списке"""
        if column.key == "image_preview":
            if hasattr(model, 'image_path') and model.image_path:
                return f'<img src="/images/{model.image_path}" style="max-width: 100px; max-height: 100px;" />'
            return "Нет изображения"
        return super().get_list_value(model, column) if hasattr(super(), 'get_list_value') else None

    def get_detail_value(self, model: Any, column: Any) -> Any:
        """Отображение изображения в детальном просмотре"""
        if column.key == "image_path" and hasattr(model, 'image_path') and model.image_path:
            return f'<img src="/images/{model.image_path}" style="max-width: 300px;" /><br/>' \
                   f'<a href="/images/{model.image_path}" target="_blank">Открыть оригинал</a>'
        return super().get_detail_value(model, column) if hasattr(super(), 'get_detail_value') else None

    def get_form_converter(self, request: Request) -> Any:
        """Добавляем виджет для загрузки изображений"""
        # Здесь можно настроить кастомный виджет для загрузки файлов
        return super().get_form_converter(request) if hasattr(super(), 'get_form_converter') else None

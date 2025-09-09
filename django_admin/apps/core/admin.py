# django_admin/apps/core/admin.py
import io
import os
from typing import Union
from django import forms
from django.contrib import admin
from django.core.files.base import ContentFile
from django.db import models
from django.utils.html import format_html
from PIL import Image

from .models import (Category, Color, Country, Drink, DrinkFood, DrinkVarietal, Food, Region, Subregion, Sweetness,
                     Varietal)


class SortedModelAdmin(admin.ModelAdmin):
    def __init__(self, *args, **kwargs):
        self.form.field_order
        super().__init__(*args, **kwargs)

    def get_fields(self, request, obj=None):
        # Получаем стандартный порядок полей от родителя
        fields = super().get_fields(request, obj)

        # Разделяем поля на категории
        required = []
        strings = []
        digitals = []
        fk_dropdown = []
        checkboxes = []
        text_memo = []

        # Определяем типы полей
        for field_name in fields:
            try:
                model_field = self.model._meta.get_field(field_name)
            except Exception:  # например, custom form field
                model_field = None

            form_field = self.form.base_fields.get(field_name)
            is_required = form_field and form_field.required

            if is_required:
                required.append(field_name)
            elif isinstance(model_field, models.CharField):
                strings.append(field_name)
            elif isinstance(model_field, Union[models.IntegerField, models.DecimalField]):
                digitals.append(field_name)
            elif isinstance(model_field, models.ForeignKey):
                fk_dropdown.append(field_name)
            elif isinstance(model_field, (models.BooleanField, models.ManyToManyField)):
                checkboxes.append(field_name)
            elif isinstance(model_field, models.TextField):
                text_memo.append(field_name)
            else:
                strings.append(field_name)  # fallback

        # Формируем итоговый порядок
        print(f'{required=}')
        print(f'{strings=}')
        print(f'{digitals=}')
        print(f'{fk_dropdown=}')
        print(f'{checkboxes=}')
        print(f'{text_memo=}')
        sorted_fields = required + strings + digitals + fk_dropdown + checkboxes + text_memo
        print(f'{sorted_fields=}')
        # Убираем дубликаты, сохраняя порядок
        seen = set()
        result = []
        for f in sorted_fields:
            if f not in seen and f in fields:
                result.append(f)
                seen.add(f)

        return result


class ImageUploadWidget(forms.ClearableFileInput):
    template_name = 'admin/widgets/image_upload.html'


class DrinkAdminForm(forms.ModelForm):
    class Meta:
        model = Drink
        fields = '__all__'
        widgets = {
            'image': ImageUploadWidget,
            'foods': forms.CheckboxSelectMultiple,  # many-to-many → чекбоксы
            'varietals': forms.CheckboxSelectMultiple,
            'category': forms.Select,               # many-to-one → выпадающий список
            'subregion': forms.Select,
            'color': forms.Select,
            'sweetness': forms.Select,
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.image and hasattr(instance.image, 'file'):
            # Обработка изображения
            img = Image.open(instance.image.file)
            # Ограничение размера до 1024x768
            img.thumbnail((1024, 768), Image.Resampling.LANCZOS)
            # Сохранение в буфер
            thumb_io = io.BytesIO()
            img_format = img.format or 'JPEG'
            img.save(thumb_io, format=img_format, quality=85)
            # Замена файла
            file_name = os.path.basename(instance.image.name)
            instance.image.save(file_name, ContentFile(thumb_io.getvalue()), save=False)
        if commit:
            instance.save()
        return instance


class DrinkFoodInline(admin.TabularInline):
    model = DrinkFood
    extra = 1
    autocomplete_fields = ('food',)


class DrinkVarietalInline(admin.TabularInline):
    model = DrinkVarietal
    extra = 1
    autocomplete_fields = ('varietal',)


@admin.register(Drink)
class DrinkAdmin(SortedModelAdmin):
    form = DrinkAdminForm
    list_display = ('title', 'alc', 'category', 'image_tag', 'get_foods')
    list_filter = ('category', 'color', 'sweetness')
    search_fields = ('title', 'title_native', 'subtitle')
    filter_horizontal = ()  # Отключаем, так как используем CheckboxSelectMultiple в форме
    readonly_fields = ('image_tag',)

    # filter_horizontal = ()  # Не работает с `through`, поэтому используем inlines
    # inlines = [DrinkFoodInline]  # ← Управление связями через вложенную форму
    filter_horizontal = ('foods',)  # ← Появятся чекбоксы
    list_display = ('title', 'get_foods')

    inlines = [DrinkVarietalInline]

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: auto;" />', obj.image.url)
        return "-"
    image_tag.short_description = 'Image'

    def get_foods(self, obj):
        return ", ".join([f.name for f in obj.foods.all()])
    get_foods.short_description = "Foods"


@admin.register(Food)
class FoodAdmin(SortedModelAdmin):
    list_display = ('name', 'name_ru', 'name_fr')
    search_fields = ('name', 'name_ru', 'name_fr')


@admin.register(Varietal)
class VarietalAdmin(SortedModelAdmin):
    list_display = ('name', 'name_ru', 'name_fr')
    search_fields = ('name', 'name_ru', 'name_fr')


@admin.register(Category)
class CategoryAdmin(SortedModelAdmin):
    pass


@admin.register(Color)
class ColorAdmin(SortedModelAdmin):
    pass


@admin.register(Country)
class CountryAdmin(SortedModelAdmin):
    pass


@admin.register(Region)
class RegionAdmin(SortedModelAdmin):
    pass


@admin.register(Subregion)
class SubregionAdmin(SortedModelAdmin):
    pass


@admin.register(Sweetness)
class SweetnessAdmin(SortedModelAdmin):
    pass

# Регистрация остальных моделей
# admin.site.register(Category)
# admin.site.register(Color)
# admin.site.register(Country)
# admin.site.register(Region)
# admin.site.register(Subregion)
# admin.site.register(Sweetness)

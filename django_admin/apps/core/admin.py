# django_admin/apps/core/admin.py
import io

from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.core.files.base import ContentFile
from PIL import Image
import os

from .models import Drink, Food, DrinkFood, Category, Color, Country, Region, Subregion, Sweetness


class ImageUploadWidget(forms.ClearableFileInput):
    template_name = 'admin/widgets/image_upload.html'


class DrinkAdminForm(forms.ModelForm):
    class Meta:
        model = Drink
        fields = '__all__'
        widgets = {
            'image': ImageUploadWidget,
            'foods': forms.CheckboxSelectMultiple,  # many-to-many → чекбоксы
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


@admin.register(Drink)
class DrinkAdmin(admin.ModelAdmin):
    form = DrinkAdminForm
    list_display = ('title', 'alc', 'category', 'image_tag', 'get_foods')
    list_filter = ('category', 'color', 'sweetness')
    search_fields = ('title', 'title_native', 'subtitle')
    filter_horizontal = ()  # Отключаем, так как используем CheckboxSelectMultiple в форме
    readonly_fields = ('image_tag',)

    filter_horizontal = ()  # Не работает с `through`, поэтому используем inlines
    inlines = [DrinkFoodInline]  # ← Управление связями через вложенную форму

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: auto;" />', obj.image.url)
        return "-"
    image_tag.short_description = 'Image'

    def get_foods(self, obj):
        return ", ".join([f.name for f in obj.foods.all()])
    get_foods.short_description = "Foods"


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_ru', 'name_fr')
    search_fields = ('name', 'name_ru', 'name_fr')


# Регистрация остальных моделей
admin.site.register(Category)
admin.site.register(Color)
admin.site.register(Country)
admin.site.register(Region)
admin.site.register(Subregion)
admin.site.register(Sweetness)

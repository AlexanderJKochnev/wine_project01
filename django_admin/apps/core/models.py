# django_admin/apps/core/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
# from django.core.files.storage import default_storage
# from PIL import Image
# from io import BytesIO
# import os

from apps.base.abstract_models import BaseFull, BaseAt, BaseDescription, BaseLang
from apps.base.fields import MongoFileField


class Category(BaseFull):
    class Meta:
        db_table = 'categories'
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")


class Color(BaseFull):
    class Meta:
        db_table = 'colors'
        verbose_name = _("Color")
        verbose_name_plural = _("Colors")


class Country(BaseFull):
    class Meta:
        db_table = 'countries'
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")


class Region(BaseFull):
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING, db_column='country_id', related_name='regions')

    class Meta:
        db_table = 'regions'
        verbose_name = _("Region")
        verbose_name_plural = _("Regions")


class Subregion(BaseFull):
    region = models.ForeignKey(Region, on_delete=models.DO_NOTHING, db_column='region_id', related_name='subregions')

    class Meta:
        db_table = 'subregions'
        verbose_name = _("Subregion")
        verbose_name_plural = _("Subregions")


class Sweetness(BaseFull):
    class Meta:
        db_table = 'sweetness'
        verbose_name = _("Sweetness")
        verbose_name_plural = _("Sweetnesses")


class Food(BaseFull):
    class Meta:
        db_table = 'foods'
        verbose_name = _("Food")
        verbose_name_plural = _("Foods")


class Drink(BaseAt, BaseDescription, BaseLang):
    title_native = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Title Native"))
    subtitle_native = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Subtitle Native"))
    title = models.CharField(max_length=255, unique=True, db_index=True, verbose_name=_("Title"))
    subtitle = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Subtitle"))
    alc = models.DecimalField(max_digits=5, decimal_places=2, null=True, verbose_name=_("Alcohol %"))
    sugar = models.DecimalField(max_digits=5, decimal_places=2, null=True, verbose_name=_("Sugar %"))
    aging = models.IntegerField(null=True, verbose_name=_("Aging"))
    sparkling = models.BooleanField(null=True, verbose_name=_("Sparkling"))
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING,
                                 db_column='category_id', related_name='drinks')
    subregion = models.ForeignKey(Subregion, on_delete=models.DO_NOTHING,
                                  db_column='subregion_id', related_name='drinks')
    color = models.ForeignKey(Color, on_delete=models.DO_NOTHING,
                              db_column='color_id', null=True, related_name='drinks')
    sweetness = models.ForeignKey(Sweetness, on_delete=models.DO_NOTHING,
                                  db_column='sweetness_id', null=True, related_name='drinks')

    # ManyToMany с Food
    # foods = models.ManyToManyField(Food, through='DrinkFood', related_name='drinks',
    # db_table='drink_food_associations')
    foods = models.ManyToManyField(Food, through='DrinkFood', related_name='drinks')
    # OneToOne с файлом в MongoDB (ссылка в Postgres)
    image = MongoFileField(upload_to='drink_images/', null=True, blank=True, verbose_name=_("Image"))

    class Meta:
        db_table = 'drinks'
        verbose_name = _("Drink")
        verbose_name_plural = _("Drinks")

    def __str__(self):
        return self.title or f"Drink {self.id}"


class DrinkFood(models.Model):
    drink = models.ForeignKey(Drink, on_delete=models.DO_NOTHING,
                              db_column='drink_id', related_name='food_associations')
    food = models.ForeignKey(Food, on_delete=models.DO_NOTHING, db_column='food_id', related_name='drink_associations')
    priority = models.IntegerField(default=0, verbose_name=_("Priority"))

    class Meta:
        db_table = 'drink_food_associations'
        unique_together = ('drink', 'food')
        managed = False  # Только чтение структуры
        verbose_name = _("Drink-Food Association")
        verbose_name_plural = _("Drink-Food Associations")

    def __str__(self):
        return f"{self.drink} - {self.food} (Prio: {self.priority})"

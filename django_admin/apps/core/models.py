# django_admin/apps/core/models.py
from apps.base.abstract_models import BaseFull
from django.db import models
from django.utils.translation import gettext_lazy as _


# from django.core.files.storage import default_storage
# from PIL import Image
# from io import BytesIO
# import os


class Category(BaseFull):
    class Meta:
        db_table = 'categories'
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        managed = False


class Color(BaseFull):
    class Meta:
        db_table = 'colors'
        verbose_name = _("Color")
        verbose_name_plural = _("Colors")
        managed = False


class Country(BaseFull):
    class Meta:
        db_table = 'countries'
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")
        managed = False


class Region(BaseFull):
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING, db_column='country_id', related_name='regions')

    class Meta:
        db_table = 'regions'
        verbose_name = _("Region")
        verbose_name_plural = _("Regions")
        managed = False


class Subregion(BaseFull):
    region = models.ForeignKey(Region, on_delete=models.DO_NOTHING, db_column='region_id', related_name='subregions')

    class Meta:
        db_table = 'subregions'
        verbose_name = _("Subregion")
        verbose_name_plural = _("Subregions")
        managed = False


class Sweetness(BaseFull):
    class Meta:
        db_table = 'sweetness'
        verbose_name = _("Sweetness")
        verbose_name_plural = _("Sweetnesses")
        managed = False


class Food(BaseFull):
    class Meta:
        db_table = 'foods'
        verbose_name = _("Food")
        verbose_name_plural = _("Foods")
        managed = False


class Varietal(BaseFull):
    class Meta:
        db_table = 'varietals'
        verbose_name = _("Varietal")
        verbose_name_plural = _("Varietals")
        managed = False


class Drink(models.Model):
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
    description = models.TextField(null=True, blank=True, verbose_name=_("Description"))
    description_ru = models.TextField(null=True, blank=True, verbose_name=_("Description (RU)"))
    description_fr = models.TextField(null=True, blank=True, verbose_name=_("Description (FR)"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))
    foods = models.ManyToManyField('Food', related_name='drinks', blank=True)
    varietals = models.ManyToManyField(Varietal, through='DrinkVarietal', related_name='drinks')
    # OneToOne с файлом в MongoDB (ссылка в Postgres)
    # image = MongoFileField(upload_to='drink_images/', null=True, blank=True, verbose_name=_("Image"))

    class Meta:
        db_table = 'drinks'
        verbose_name = _("Drink")
        verbose_name_plural = _("Drinks")
        managed = False

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
        managed = False

    def __str__(self):
        return f"{self.drink} - {self.food} (Prio: {self.priority})"


class DrinkVarietal(models.Model):
    drink = models.ForeignKey(Drink, on_delete=models.DO_NOTHING,
                              db_column='drink_id', related_name='varietal_associations')
    varietal = models.ForeignKey(Varietal, on_delete=models.DO_NOTHING,
                                 db_column='varietal_id', related_name='drink_associations')
    percentage = models.IntegerField(default=1, verbose_name=_("Percentage"))

    class Meta:
        db_table = 'drink_varietal_associations'
        unique_together = ('drink', 'varietal')
        managed = False  # Только чтение структуры
        verbose_name = _("Drink-Varietable Association")
        verbose_name_plural = _("Drink-Varietables Associations")
        managed = False

    def __str__(self):
        return f"{self.drink} - {self.varietal} (Prio: {self.percentage})"

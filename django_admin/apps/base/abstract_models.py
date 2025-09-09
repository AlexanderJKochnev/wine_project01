# django_admin/apps/base/abstract_models.py
from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseAt(models.Model):
    """Время создания/изменения"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    class Meta:
        abstract = True


class BaseInt(models.Model):
    """Поля на английском"""
    name = models.CharField(max_length=255, unique=True, null=False, db_index=True, verbose_name=_("Name"))
    description = models.TextField(null=True, blank=True, verbose_name=_("Description"))

    class Meta:
        abstract = True


class BaseDescription(models.Model):
    """Мультиязычные описания"""
    description_ru = models.TextField(null=True, blank=True, verbose_name=_("Description (RU)"))
    description_fr = models.TextField(null=True, blank=True, verbose_name=_("Description (FR)"))

    class Meta:
        abstract = True


class BaseLang(BaseDescription):
    """Мультиязычные названия"""
    name_ru = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Name (RU)"))
    name_fr = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Name (FR)"))

    class Meta:
        abstract = True


class BaseFull(BaseInt, BaseAt, BaseLang):
    """Полная базовая модель"""
    class Meta:
        abstract = True

    def __str__(self):
        return self.name or f"{self._meta.verbose_name} {self.id}"

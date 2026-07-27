# app.core.admin.config.py
"""
starlette-admin
"""
import json

from fastapi import FastAPI
from jinja2 import ChoiceLoader, Environment, FileSystemLoader
from starlette.templating import Jinja2Templates
from starlette_admin import CustomView, RequestAction
from starlette_admin.contrib.sqla import Admin
from starlette_admin.helpers import get_file_icon
from starlette_admin.i18n import (get_locale, get_locale_display_name, get_timezone, get_timezone_display_name, gettext,
                                  I18nConfig, ngettext)
from starlette_admin.views import BaseModelView, DropDown, Link

from app.admin.auth import AdminAuthProvider
from app.admin.views import CategoryView, CountryView, FoodView, OtherView, ParcelView, \
    ProducerTitleView, ProducerView, RegionView, SourceView, SubcategoryView, SubregionView, SuperFoodView, TestView, \
    UserAdminView
from app.auth.models import User
from app.support import BaseIngredient, Body, Category, Country, Food, Glassware, Producer, ProducerTitle, Region, \
    Scale, Source, Subcategory, Subregion, Superfood, TastingNote
from app.support.vllm.model import TranslateHelper


class CustomAdmin(Admin):
    """
        переписываем def _setup_templates_ что бы не лез за дефолтными шаблонами
    """

    def _setup_templates(self) -> None:
        env = Environment(
            loader=ChoiceLoader(
                [
                    FileSystemLoader(self.templates_dir),
                    # PackageLoader("starlette_admin", "templates"),
                    # PrefixLoader(
                    #    {
                    #         "@starlette-admin": PackageLoader(
                    #             "starlette_admin", "templates"
                    #         ),
                    #     }
                    # ),
                ]
            ),
            extensions=["jinja2.ext.i18n"],
            autoescape=True,
        )
        templates = Jinja2Templates(env=env)

        # globals
        templates.env.globals["views"] = self._views
        templates.env.globals["app_title"] = self.title
        templates.env.globals["is_auth_enabled"] = self.auth_provider is not None
        templates.env.globals["__name__"] = self.route_name
        templates.env.globals["logo_url"] = self.logo_url
        templates.env.globals["login_logo_url"] = self.login_logo_url
        templates.env.globals["favicon_url"] = self.favicon_url
        templates.env.globals["custom_render_js"] = self.custom_render_js
        templates.env.globals["get_locale"] = get_locale
        templates.env.globals["get_locale_display_name"] = get_locale_display_name
        templates.env.globals["i18n_config"] = self.i18n_config or I18nConfig()
        templates.env.globals["get_timezone"] = get_timezone
        templates.env.globals["get_timezone_display_name"] = get_timezone_display_name
        templates.env.globals["timezone_config"] = self.timezone_config
        # filters
        templates.env.filters["is_custom_view"] = lambda r: isinstance(r, CustomView)
        templates.env.filters["is_link"] = lambda res: isinstance(res, Link)
        templates.env.filters["is_model"] = lambda res: isinstance(res, BaseModelView)
        templates.env.filters["is_dropdown"] = lambda res: isinstance(res, DropDown)
        templates.env.filters["get_admin_user"] = (
            self.auth_provider.get_admin_user if self.auth_provider else None
        )
        templates.env.filters["get_admin_config"] = (
            self.auth_provider.get_admin_config if self.auth_provider else None
        )
        templates.env.filters["tojson"] = lambda data: json.dumps(data, default=str)
        templates.env.filters["file_icon"] = get_file_icon
        templates.env.filters["to_model"] = self._find_model_from_identity
        templates.env.filters["is_iter"] = lambda v: isinstance(v, (list, tuple))
        templates.env.filters["is_str"] = lambda v: isinstance(v, str)
        templates.env.filters["is_dict"] = lambda v: isinstance(v, dict)
        templates.env.filters["ra"] = RequestAction
        # install i18n
        templates.env.install_gettext_callables(gettext, ngettext, True)  # type: ignore
        self.templates = templates


def setup_starlette_admin(app: FastAPI, async_engine) -> Admin:
    """Инициализирует админку, принимая асинхронный AsyncEngine."""

    admin = CustomAdmin(
        engine=async_engine,  # Передаем ваш асинхронный engine
        title="Админ панель", base_url="/panel",
        templates_dir="templates",  # Указывает на вашу папку с измененным layout.html
        statics_dir="statics",  # Указывает на папку со скачанными CSS/JS файлами
        auth_provider=AdminAuthProvider(),
        route_name="admin"
    )

    admin.add_view(UserAdminView(User, identity="user", label="Пользователи"))
    # admin.add_view(SomeView(TranslateHelper, identity="translatehelper", label="Словарь"))
    admin.add_view(SourceView(Source, identity="source", label="Источники данных"))
    admin.add_view(CategoryView(Category, identity="category", label="Категории"))
    admin.add_view(SubcategoryView(Subcategory, identity="subcategory", label="Подкатегории"))
    # Geography
    admin.add_view(CountryView(Country, identity='country', label='Страны'))
    admin.add_view(RegionView(Region, identity='region', label='Регионы'))
    admin.add_view(SubregionView(Subregion, identity='subregion', label='Cубрегионы'))
    admin.add_view(SubregionView(Subregion, identity='site', label='Терруары'))
    admin.add_view(ParcelView(Subregion, identity='parcel', label='Миктротерруары'))
    # Producres
    admin.add_view(ProducerTitleView(ProducerTitle, identity='producertitle', label='Тип производителя'))
    admin.add_view(ProducerView(Producer, identity='producer', label='Производитель'))
    # Food
    admin.add_view(SuperFoodView(Superfood, identity='superfood', label='Тип продуктов'))
    admin.add_view(FoodView(Food, identity='food', label='Продукты'))
    # Other
    admin.add_view(OtherView(BaseIngredient, identity='baseingredient', label='Основные ингредиенты'))
    admin.add_view(OtherView(Body, identity='body', label='Тело вина'))
    admin.add_view(OtherView(Glassware, identity='glassware', label='Бокалы'))
    admin.add_view(OtherView(Scale, identity='scale', label='Scale'))
    admin.add_view(OtherView(TastingNote, identity='tastingnote', label='Вкусовые оттенки'))
    admin.add_view(TestView(TranslateHelper, identity="translatehelper", label="TranslateHelper"))
    admin.mount_to(app)

    return admin

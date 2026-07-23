# app.admin.models.py

from fastapi_amis_admin.admin import ModelAdmin
from fastapi_amis_admin.admin.site import AdminSite
from app.auth.models import User


class UserAdmin(ModelAdmin):
    model = User
    page_schema = 'Пользователи'
    list_display = ['id', 'username', 'email', 'is_active', 'is_superuser']
    search_fields = ['username', 'email']


def register_all_models(site: AdminSite):
    site.register_admin(UserAdmin)
    print("✅ Все модели зарегистрированы в админке")

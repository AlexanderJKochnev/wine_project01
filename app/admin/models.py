# app.admin.models.py

from fastapi_amis_admin.admin import ModelAdmin
from fastapi_amis_admin.admin.site import AdminSite

# Импортируем ваши модели
from app.auth.models import User


# Добавьте сюда все остальные ваши модели
# from app.products.models import Product, Category
# from app.orders.models import Order
# и т.д.


# ========== 1. РЕГИСТРАЦИЯ МОДЕЛИ ПОЛЬЗОВАТЕЛЕЙ ==========
class UserAdmin(ModelAdmin):
    """Админка для модели User"""
    model = User
    page_schema = 'Пользователи'

    # Какие поля показывать в списке
    list_display = ['id', 'username', 'email', 'is_active', 'is_superuser', 'created_at']

    # По каким полям искать
    search_fields = ['username', 'email']

    # Поля, которые можно редактировать в форме
    fields = ['username', 'email', 'is_active', 'is_superuser']

    # Поля только для чтения
    readonly_fields = ['id', 'created_at', 'updated_at']


# ========== 2. ФУНКЦИЯ ДЛЯ РЕГИСТРАЦИИ ВСЕХ МОДЕЛЕЙ ==========
def register_all_models(site: AdminSite):
    """
    Регистрирует все модели в админке
    """
    # Регистрируем пользователей
    site.register_admin(UserAdmin)

    # ДОБАВЛЯЙТЕ СВОИ МОДЕЛИ НИЖЕ:
    # site.register_admin(ProductAdmin)
    # site.register_admin(CategoryAdmin)
    # site.register_admin(OrderAdmin)

    print("✅ Все модели зарегистрированы в админке")

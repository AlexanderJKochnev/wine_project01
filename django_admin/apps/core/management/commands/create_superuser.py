# django_admin/apps/core/management/commands/sreate_superuser.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django_app.db_config import settings_db


class Command(BaseCommand):
    help = 'Создаёт суперпользователя для Django (из переменных окружения)'

    def handle(self, *args, **options):
        email = settings_db.ADMIN_EMAIL
        password = settings_db.ADMIN_PASSWORD
        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                username=email,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f'Суперпользователь {email} создан'))
        else:
            self.stdout.write('Суперпользователь уже существует')

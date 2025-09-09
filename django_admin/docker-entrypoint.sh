#!/bin/bash

set -e

echo "🔧 Применение миграций Django..."
python manage.py migrate --noinput

echo "🔐 Создание суперпользователя..."
python manage.py create_superuser

echo "📦 Сборка статики..."
python manage.py collectstatic --noinput --clear

echo "🚀 Запуск Django сервера..."
exec python manage.py runserver 0.0.0.0:8000
#!/bin/bash

# Определяем путь к директории скрипта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Путь к .env файлу
ENV_FILE="$SCRIPT_DIR/.env"

# Проверяем, существует ли .env файл
if [[ ! -f "$ENV_FILE" ]]; then
    echo "Ошибка: Файл .env не найден по пути: $ENV_FILE"
    exit 1
fi

# Загружаем переменные из .env
set -a  # Автоматически экспортирует все переменные
source "$ENV_FILE"
set +a  # Отключаем автоматический экспорт

# Дамп с использованием .pgpass или PGPASSWORD
docker compose exec wine_host pg_dump "postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}/${POSTGRES_DB}" -F c -f /tmp/backup.dump

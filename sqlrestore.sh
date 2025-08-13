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

# Восстановление
# docker compose exec wine_host pg_restore -d wine_db -h localhost -p 5432 -U wine --clean /tmp/backup.dump
docker compose exec ${POSTGRES_HOST} pg_restore -d ${POSTGRES_DB} -h localhost -p ${POSTGRES_PORT} -U ${POSTGRES_USER} --clean /tmp/backup.dump

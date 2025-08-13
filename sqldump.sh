#!/bin/bash

# Загрузка переменных из .env
set -a
source .env
set +a

# Дамп с использованием .pgpass или PGPASSWORD
docker compose exec wine_host pg_dump "postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}/${POSTGRES_DB}" -F c -f /tmp/backup.dump

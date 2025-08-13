#!/bin/bash

# Загрузка переменных из .env
set -a
source .env
set +a

# Восстановление
# docker compose exec wine_host pg_restore -d wine_db -h localhost -p 5432 -U wine --clean /tmp/backup.dump
docker compose exec ${POSTGRES_HOST} pg_restore -d ${POSTGRES_DB} -h localhost -p ${POSTGRES_PORT} -U ${POSTGRES_USER} --clean /tmp/backup.dump

#!/bin/bash

# Загружаем переменные из .env файла
source .env
# или
. .env

# Теперь переменные доступны в скрипте
echo "Database host: $DB_HOST"
echo "Database user: $DB_USER"
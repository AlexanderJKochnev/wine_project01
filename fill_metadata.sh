#!/bin/bash
# создание trigram-indexes
# Определяем путь к директории скрипта
docker exec -i wine_host psql -U wine -d wine_db < scripts/jsonb_raw.sql

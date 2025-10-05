#!/bin/bash
# очистка базы данных postgresql
# Определяем путь к директории скрипта
docker exec -i wine_host psql -U wine -d wine_db < scripts/clear_data.sql

docker exec mongo mongo wine_database --eval "
db.images.deleteMany({});
"
# docker exec -i your-postgres-container psql -U your_user -d your_db < clear_data.sql
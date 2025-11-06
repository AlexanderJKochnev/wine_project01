#!/bin/bash

# миграции в mongodb - создание thumbnails
# docker compose exec app alembic revision --autogenerate -m 'Restart revision'
# docker compose exec app alembic upgrade head
# docker compose exec app python -m app.mongodb.migration
docker compose exec app python app.mongodb.migration
# alembic revision --autogenerate -m 'Restart revision'
# alembic upgrade head
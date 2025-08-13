#!/bin/bash

# миграции в postgersql после обновления структуры models
docker compose exec app alembic revision --autogenerate -m 'Restart revision'
docker compose exec app alembic upgrade head
# alembic revision --autogenerate -m 'Restart revision'
# alembic upgrade head
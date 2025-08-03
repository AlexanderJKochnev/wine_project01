#!/bin/bash

# миграции в postgersql после обновления структуры models
docker compose exec app alembic revision --autogenerate -m 'Initial revision'
docker compose exec app alembic upgrade head

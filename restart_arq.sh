#!/bin/bash
# перезапуск arq-worker

set -e

# echo "🔁 Останавливаем arq-worker..."
# docker-compose stop arq-worker

# echo "🧹 Удаляем старый контейнер (если есть)..."
# docker-compose rm -f arq-worker

# echo "🚀 Пересобираем образ (опционально)..."
# docker-compose build --no-cache arq-worker

echo "▶️ Запускаем arq-worker..."
docker compose up -d arq-worker

echo "✅ arq-worker перезапущен!"
docker compose logs arq-worker
# запуск со слежением
# docker-compose logs -f arq-worker
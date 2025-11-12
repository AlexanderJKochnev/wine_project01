# DOCS/ningx.md
# 0. Делаем скрипт исполняемым (Linux)
chmod +x scripts/generate-certs.sh
# 1. Генерируем сертификат
./scripts/generate-certs.sh

# 2. Запускаем всё (кроме билдера)
docker-compose up -d --no-deps nginx wine_host adminer app django

# 3. Собираем клиентский образ
docker-compose up client-image-builder

# 4. Экспортируем образ (можно раздать коллегам)
docker save your-project_client-image-builder:latest | gzip > trusted-client.tar.gz
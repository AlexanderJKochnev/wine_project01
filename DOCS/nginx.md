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

# 5. Настройка CORS
app.main.py 
см. CORS

# 6. Настройка PREACT
preact-front/src/config/api.ts
vite.config.js
    Nginx: Создано два server_name.
    FastAPI: Включен CORSMiddleware с указанием abc8888.ru.
    Preact: API_BASE_URL указывает на http://api.abc8888.ru.

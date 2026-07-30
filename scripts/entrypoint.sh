#!/bin/sh
# скрипт для контроля за ssl сертификатами
set -e

DOMAIN="abc8888.ru"
SUBDOMAIN="api.abc8888.ru"
EMAIL="admin@abc8888.ru"
CERT_PATH="/etc/letsencrypt/live/$DOMAIN/fullchain.pem"

echo "Проверка наличия SSL сертификатов для $DOMAIN..."

# 1. Проверка наличия сертификатов в Volume
if [ ! -f "$CERT_PATH" ]; then
    echo "Сертификаты не найдены. Запуск процесса получения..."

    # Запускаем временный nginx для прохождения проверки Let's Encrypt (HTTP-01 challenge)
    nginx -g "daemon off;" &
    NGINX_PID=$!
    sleep 5

    certbot certonly --webroot -w /var/www/certbot \
        --non-interactive --agree-tos --email $EMAIL \
        -d $DOMAIN -d $SUBDOMAIN

    echo "Сертификаты получены. Останавливаем временный Nginx..."
    kill $NGINX_PID
    sleep 2
else
    echo "Сертификаты уже существуют в Volume."
fi

# 2. Проверка и настройка Cron для автообновления
if ! crontab -l | grep -q "certbot renew"; then
    echo "Настройка задачи обновления в crontab..."
    echo "0 12 * * * certbot renew --quiet --post-hook 'nginx -s reload'" >> /var/spool/cron/crontabs/root
fi

# Запуск cron в фоновом режиме
crond

# Запуск основного Nginx
echo "Запуск Nginx в штатном режиме..."
exec nginx -g "daemon off;"

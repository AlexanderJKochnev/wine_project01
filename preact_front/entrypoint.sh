#!/bin/sh
set -e

DOMAIN="abc8888.ru"
SUBDOMAIN="api.abc8888.ru"
EMAIL="admin@abc8888.ru"
CERT_DIR="/etc/letsencrypt/live/$DOMAIN"

echo "[PRE-START] Проверка SSL для $DOMAIN..."

# 1. Получаем сертификаты, если их нет
if [ ! -f "$CERT_DIR/fullchain.pem" ]; then
    echo "[PRE-START] Сертификаты не найдены. Запуск Certbot в режиме standalone..."

    # Certbot сам поднимет сервер на 80 порту, получит ключи и закроется
    certbot certonly --standalone \
        --non-interactive --agree-tos --email $EMAIL \
        -d $DOMAIN -d api.$DOMAIN

    echo "[PRE-START] Сертификаты успешно получены."
else
    echo "[PRE-START] Сертификаты уже на месте."
fi

# 2. Настройка Cron для автообновления
if ! crontab -l 2>/dev/null | grep -q "certbot renew"; then
    echo "0 12 * * * certbot renew --quiet --post-hook 'nginx -s reload'" >> /var/spool/cron/crontabs/root
fi
crond -b

echo "[PRE-START] Подготовка завершена. Передаем управление Nginx."

# Передаем управление стандартному entrypoint'у Nginx,
# который выполнит все свои 10-listen-on-ipv6-by-default.sh и прочее
exec /docker-entrypoint.sh "$@"

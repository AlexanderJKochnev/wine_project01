# --- ЭТАП 1: Базовые зависимости (Base) ---
FROM node:20-alpine AS build-stage
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
RUN apk add --no-cache certbot

# Stage 2: Раздача статики через Nginx
FROM nginx:stable-alpine
# Копируем билд из первого стейджа
COPY --from=build-stage /app/dist /usr/share/nginx/html
# Копируем конфиг
RUN apk add --no-cache certbot
RUN mkdir -p /var/www/certbot
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh


EXPOSE 80
ENTRYPOINT ["/entrypoint.sh"]
# CMD ["nginx", "-g", "daemon off;"]


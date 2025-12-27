# --- ЭТАП 1: Базовые зависимости (Base) ---
FROM node:20-alpine AS build-stage
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Раздача статики через Nginx
FROM nginx:stable-alpine
# Копируем билд из первого стейджа
COPY --from=build-stage /app/dist /usr/share/nginx/html
# Копируем конфиг (создадим его ниже)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]


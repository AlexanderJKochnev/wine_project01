# --- ЭТАП 1: Базовые зависимости (Base) ---
FROM node:20-alpine AS base
WORKDIR /app
COPY package*.json ./

# --- ЭТАП 2: Разработка (Development) ---
# Используется для локальной разработки
FROM base AS development
RUN npm install
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# --- ЭТАП 3: Сборка (Build) ---
# Здесь мы компилируем проект в статику
FROM base AS build
RUN npm ci
COPY . .
RUN npm run build

# --- ЭТАП 4: Продакшн (Production) ---
# Финальный этап: берем только готовые файлы и отдаем их через быстрый сервер (напр. Nginx)
FROM nginx:stable-alpine AS production
# Копируем билд из этапа build в папку nginx
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

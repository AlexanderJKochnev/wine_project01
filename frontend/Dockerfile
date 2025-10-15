# Build stage
FROM node:18-alpine as builder

# Устанавливаем pnpm
RUN npm install -g pnpm

WORKDIR /app

# Копируем файлы зависимостей
COPY package.json pnpm-lock.yaml ./

# Устанавливаем зависимости
RUN pnpm install

# Копируем исходный код
COPY . .

# Собираем приложение
RUN BROWSERSLIST_DISABLE_CACHE=1 pnpm run build
# RUN pnpm run build

# Production stage
FROM nginx:alpine

# Копируем собранное приложение в nginx
COPY --from=builder /app/build /usr/share/nginx/html

# Копируем конфиг nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
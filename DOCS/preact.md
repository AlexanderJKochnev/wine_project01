# пробуем вместо React
### https://chat.qwen.ai/c/ba7afb0a-f974-4626-a278-3c62f36197ac

1. Начинаем из корня:
2. npm create preact@latest preact_front
   cd my-preact-app
   1. Typescript Yes
   2. Use router Yes
   3. prefended app (SSG) No
   4. use ESLint Yes
3. touch Dockerfile.dev (после настройки сделать обычный)
4. добавить service preact в docker-compose.yaml
5. package.json заменить "dev": "vite --host 0.0.0.0 --port 5173"
6. ...
7. установка mui
   1. npm install @mui/material @emotion/react @emotion/styled
   2. npm install @mui/x-data-grid
8. 

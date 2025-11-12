https://chat.deepseek.com/a/chat/s/aab1552b-b8a3-4330-a2e9-1a04c4518f4f

cd frontend
npm install -g pnpm
make sure that package.json exists
pnpm install

все что выше не труьуется - все запускается в контейнере
в package.json 
в prod замениить строку
"start": "react-scripts start --host 0.0.0.0",
на:
"start": "react-scripts start",

1. React дико конфликтует с docker - ни один встороенный сервер не работает в docker
2. не вестить на npm pnpm - глючные пакетные менеджеры (по крайней мере для React)
3. Тема React закрыта
cd frontend

# Очистим предыдущие сборки
rm -rf build/ node_modules/

# Установим зависимости и соберем
pnpm install
pnpm run build

# Проверим что создалось
echo "=== Build folder structure ==="
ls -la build/

echo "=== Static folder structure ==="
ls -la build/static/

echo "=== JS files ==="
find build/static -name "*.js" | head -10

echo "=== Total size ==="
du -sh build/
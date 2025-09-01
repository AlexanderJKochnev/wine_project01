#!/bin/sh
set -e

# Проверяем обязательные переменные
: "${MONGODB_USER_NAME:?MONGODB_USER_NAME not set}"
: "${MONGODB_USER_PASSWORD:?MONGODB_USER_PASSWORD not set}"
: "${MONGODB_REPLICA_SET:?MONGODB_REPLICA_SET not set}"
: "${MONGODB_REPLICA_SET_HOST:?MONGODB_REPLICA_SET_HOST not set}"
: "${MONGODB_PORT:?MONGODB_PORT not set}"
: "${MONGODB_DATABASE_AUTH_NAME:?MONGODB_DATABASE_AUTH_NAME not set}"

KEYFILE=/etc/mongo.key

echo "🔐 Генерируем keyfile..."
head -c 756 /dev/urandom | base64 > "$KEYFILE"
chmod 600 "$KEYFILE"

echo "🚀 Запускаем mongod (этап 1: без auth)..."
mongod \
  --replSet "${MONGODB_REPLICA_SET}" \
  --bind_ip_all \
  --port "${MONGODB_PORT}" \
  --dbpath /data/db \
  --fork \
  --logpath /tmp/mongod-init.log

echo "⏳ Ждём готовности mongod..."
timeout=15
while ! mongo --host "127.0.0.1" --port "${MONGODB_PORT}" --eval "db.adminCommand('ping')" >/dev/null 2>&1; do
  sleep 1
  timeout=$((timeout - 1))
  if [ "$timeout" -le 0 ]; then
    echo "❌ mongod не отвечает"
    pkill mongod
    exit 1
  fi
done
echo "✅ mongod запущен"

echo "🔍 Инициализируем Replica Set..."
RS_INIT_CHECK=$(mongo --host "127.0.0.1" --port "${MONGODB_PORT}" --quiet --eval "try { rs.status().ok } catch(e) { 0 }")
if [ "$RS_INIT_CHECK" != "1" ]; then
  echo "🧱 Инициализируем rs.initiate..."
  mongo --host "127.0.0.1" --port "${MONGODB_PORT}" --eval "
    rs.initiate({
      _id: '${MONGODB_REPLICA_SET}',
      members: [{ _id: 0, host: '${MONGODB_REPLICA_SET_HOST}:${MONGODB_PORT}' }]
    });
  "
  echo "✅ Replica Set инициализирован"
else
  echo "ℹ️ Replica Set уже инициализирован"
fi

echo "⏳ Ожидание PRIMARY..."
timeout=30
while true; do
  PRIMARY=$(mongo --host "127.0.0.1" --port "${MONGODB_PORT}" --quiet --eval "rs.isMaster().ismaster" 2>/dev/null || echo "false")
  if [ "$PRIMARY" = "true" ]; then
    echo "✅ Node стал PRIMARY"
    break
  fi
  sleep 1
  timeout=$((timeout - 1))
  if [ "$timeout" -le 0 ]; then
    echo "❌ Таймаут ожидания PRIMARY"
    exit 1
  fi
done

echo "👤 Проверяем и создаём пользователя..."
EXISTS=$(mongo --host "127.0.0.1" --port "${MONGODB_PORT}" --quiet --eval "
  db.getSiblingDB('${MONGODB_DATABASE_AUTH_NAME}').system.users.find({user:'${MONGODB_USER_NAME}'}).count()
")
if [ "$EXISTS" -eq 0 ]; then
  mongo --host "127.0.0.1" --port "${MONGODB_PORT}" "${MONGODB_DATABASE_AUTH_NAME}" --eval "
    db.createUser({
      user: '${MONGODB_USER_NAME}',
      pwd: '${MONGODB_USER_PASSWORD}',
      roles: [{ role: 'root', db: '${MONGODB_DATABASE_AUTH_NAME}' }]
    });
  "
  echo "✅ Пользователь создан"
else
  echo "ℹ️ Пользователь уже существует"
fi

echo "🔄 Останавливаем временный mongod..."
mongo --host "127.0.0.1" --port "${MONGODB_PORT}" --eval "db.getSiblingDB('admin').shutdownServer()" || true
sleep 5

echo "🔐 Запускаем финальный mongod с auth и keyFile..."
exec mongod \
  --replSet "${MONGODB_REPLICA_SET}" \
  --auth \
  --keyFile "$KEYFILE" \
  --bind_ip_all \
  --port "${MONGODB_PORT}" \
  --dbpath /data/db
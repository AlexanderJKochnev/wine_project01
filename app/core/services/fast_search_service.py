# app.core.service.fast_search_service.py

import asyncio
import re
import threading
from typing import List
import redis
from datasketch import MinHash, MinHashLSH

from app.core.config.project_config import settings

# --- КОНФИГУРАЦИЯ ---
REDIS_HOST = "search_cache"  # Имя сервиса из docker-compose
REDIS_PORT = settings.REDIS_PORT
REDIS_PASSWORD = settings.REDIS_PWD

LSH_THRESHOLD = 0.5  # Порог схожести Жаккара (50%)
NUM_PERM = 128  # Размер сигнатуры (128 чисел = ~1.5 Кб на строку)

# --- ИНИЦИАЛИЗАЦИЯ ПОДКЛЮЧЕНИЙ ---
redis_client = redis.Redis(
    host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=0
)

# Инициализируем LSH с бэкендом в Redis
lsh = MinHashLSH(
    threshold=LSH_THRESHOLD, num_perm=NUM_PERM,
    storage_config={'type': 'redis', 'config': {'redis': redis_client}}
)

# Блокировка для обеспечения потокобезопасности при записи воркерами/background tasks
lsh_write_lock = threading.Lock()


def sync_build_minhash(text: str) -> MinHash:
    """
    Чистая синхронная функция CPU-интенсивных вычислений.
    Разбивает текст на 4-граммы и строит MinHash.
    """
    m = MinHash(num_perm=NUM_PERM)
    if not text:
        return m

    # Нормализация: только буквы нижнего регистра, цифры и пробелы
    clean_text = re.sub(r'[^a-zа-я0-9\s]', '', text.lower())

    # Генерация 4-грамм символов
    shingles = [clean_text[i:i + 4] for i in range(len(clean_text) - 3)]

    for shingle in shingles:
        m.update(shingle.encode('utf-8'))
    return m


async def async_build_minhash(text: str) -> MinHash:
    """Обертка для безопасного запуска расчета хэшей в пуле потоков FastAPI"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, sync_build_minhash, text)


# === ИНТЕРФЕЙС ДЛЯ BACKGROUND TASKS (СИНХРОННЫЙ / ПОТОКОБЕЗОПАСНЫЙ) ===

def update_entity_index(entity_id: int, full_text: str) -> None:
    """
    Метод для вызова внутри фоновой задачи FastAPI (BackgroundTasks).
    Принимает ID записи и обновленный агрегированный текст из Postgres.
    """
    new_hash = sync_build_minhash(full_text)
    key = f"doc_{entity_id}"

    with lsh_write_lock:
        try:
            lsh.remove(key)
        except ValueError:
            pass  # Игнорируем, если ключа еще не было в индексе (новая запись)

        lsh.insert(key, new_hash)


def remove_entity_index(entity_id: int) -> None:
    """Метод для удаления сущности из индекса при удалении строки из Postgres"""
    key = f"doc_{entity_id}"
    with lsh_write_lock:
        try:
            lsh.remove(key)
        except ValueError:
            pass


# === ИНТЕРФЕЙС ДЛЯ ХЕНДЛЕРОВ API (АСИНХРОННЫЙ) ===

async def search_similar_ids(user_query: str) -> List[int]:
    """
    Асинхронный поиск похожих ID.
    Не блокирует event loop FastAPI во время тяжелых расчетов MinHash.
    """
    if not user_query.strip():
        return []

    # Переносим расчет хэша запроса в отдельный поток, чтобы не фризить API
    query_hash = await async_build_minhash(user_query)

    # lsh.query() делает быстрые точечные обращения к Redis,
    # run_in_executor защищает от микро-фризов сетевого ввода-вывода
    loop = asyncio.get_running_loop()
    matched_keys = await loop.run_in_executor(None, lsh.query, query_hash)

    # Парсим строковые ключи 'doc_123' обратно в числовые ID для Postgres
    return [int(key.split('_')[1]) for key in matched_keys]

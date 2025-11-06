import functools
import time
import asyncio
from typing import Any, Optional, Callable, Dict
from pymemcache.client.base import Client as SyncClient
from pymemcache import serde
import inspect
from app.core.config.project_config import settings


class AsyncMemcachedCache:
    def __init__(self):
        self.client: Optional[SyncClient] = None
        self.pool = None
    
    async def init_memcached(self):
        """Инициализация подключения к Memcached"""
        try:
            # Используем thread pool для асинхронной работы с синхронным клиентом
            self.client = SyncClient(
                    (settings.MEMCACHED_HOST, settings.MEMCACHED_PORT), connect_timeout = 2, timeout = 2,
                    no_delay = True, serializer = serde.python_memcache_serializer,
                    deserializer = serde.python_memcache_deserializer
                    )
            
            # Тестируем подключение
            self.client.set('test', 'connection', expire = 1)
            print("Memcached connected successfully")
        except Exception as e:
            print(f"Memcached connection error: {e}")
            self.client = None
    
    async def close(self):
        """Закрытие подключения"""
        if self.client:
            self.client.close()
    
    async def get_binary(self, key: str) -> Optional[bytes]:
        """Получить бинарные данные из Memcached"""
        if not self.client:
            return None
        
        start_time = time.time()
        try:
            # Используем thread pool для асинхронной работы
            result = await asyncio.get_event_loop().run_in_executor(
                    None, self.client.get, key
                    )
            elapsed = time.time() - start_time
            if elapsed > 0.05:  # Логируем медленные запросы
                print(f"Memcached GET: {elapsed:.3f}s for key: {key}")
            return result
        except Exception as e:
            print(f"Memcached GET error: {e}")
            return None
    
    async def set_binary(self, key: str, value: bytes, expire: int = 3600) -> bool:
        """Сохранить бинарные данные в Memcached"""
        if not self.client:
            return False
        
        start_time = time.time()
        try:
            success = await asyncio.get_event_loop().run_in_executor(
                    None, self.client.set, key, value, expire
                    )
            elapsed = time.time() - start_time
            if elapsed > 0.05:
                print(f"Memcached SET: {elapsed:.3f}s, size: {len(value)} bytes")
            return success
        except Exception as e:
            print(f"Memcached SET error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Удалить данные из Memcached"""
        if not self.client:
            return False
        try:
            return await asyncio.get_event_loop().run_in_executor(
                    None, self.client.delete, key
                    )
        except Exception:
            return False


# Глобальный экземпляр Memcached кэша
memcached_cache = AsyncMemcachedCache()


def cache_image_memcached(
        prefix: str = "image", expire: int = 3600, key_params: Optional[list] = None
        ):
    """
    Декоратор для кэширования изображений в Memcached
    """
    
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{prefix}:{func.__module__}:{func.__name__}"
            
            if key_params:
                param_values = []
                for param in key_params:
                    if param in kwargs:
                        param_values.append(f"{param}:{kwargs[param]}")
                    else:
                        sig = inspect.signature(func)
                        bound_args = sig.bind(*args, **kwargs)
                        bound_args.apply_defaults()
                        if param in bound_args.arguments:
                            param_values.append(f"{param}:{bound_args.arguments[param]}")
                
                if param_values:
                    cache_key += ":" + ":".join(param_values)
            
            start_time = time.time()
            
            # Пытаемся получить данные из Memcached
            cached_data = await memcached_cache.get_binary(cache_key)
            if cached_data is not None:
                elapsed = time.time() - start_time
                print(f"Memcached HIT: {elapsed:.3f}s for {cache_key}")
                
                return {"content": cached_data, "filename": f"cached_{cache_key.split(':')[-1]}",
                        "content_type": "image/png", "from_cache": True}
            
            # Кэш-промах, выполняем функцию
            result = await func(*args, **kwargs)
            
            # Сохраняем в Memcached асинхронно
            if (isinstance(result, dict) and "content" in result and isinstance(result["content"], bytes)):
                asyncio.create_task(
                        memcached_cache.set_binary(cache_key, result["content"], expire)
                        )
                result["from_cache"] = False
            
            elapsed = time.time() - start_time
            print(f"Memcached MISS: {elapsed:.3f}s for {cache_key}")
            
            return result
        
        return wrapper
    
    return decorator


def invalidate_memcached_pattern(patterns: list[str]):
    """
    Инвалидация кэша в Memcached (ограниченная поддержка паттернов)
    """
    
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            # Memcached не поддерживает поиск по паттернам,
            # поэтому инвалидируем только конкретные ключи
            # В реальном приложении нужно вести индекс ключей
            for pattern in patterns:
                if '*' not in pattern:  # Инвалидируем только конкретные ключи
                    await memcached_cache.delete(pattern)
            
            return result
        
        return wrapper
    
    return decorator
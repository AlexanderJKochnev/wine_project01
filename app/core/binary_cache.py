import functools
from typing import Any, Optional, Callable, Dict
from redis.asyncio import Redis, ConnectionPool
from app.core.config.project_config import settings
import inspect


class BinaryRedisCache:
    def __init__(self):
        self.redis: Optional[Redis] = None
    
    async def init_redis(self):
        """Инициализация подключения к Redis для бинарных данных"""
        self.pool = ConnectionPool(
                host = settings.REDIS_HOST, port = settings.REDIS_PORT, decode_responses = False, max_connections = 20,
                socket_connect_timeout = 2,  # Уменьшаем таймауты
                socket_timeout = 2, retry_on_timeout = True, health_check_interval = 30
                )
        self.redis = Redis(connection_pool = self.pool)
        
        # Тестируем подключение
        try:
            await self.redis.ping()
            print("Redis binary cache connected successfully")
        except Exception as e:
            print(f"Redis connection error: {e}")
    
    async def close(self):
        if self.redis:
            await self.redis.close()
    
    async def get_binary(self, key: str) -> Optional[bytes]:
        """Получить бинарные данные из кэша"""
        if not self.redis:
            return None
        try:
            return await self.redis.get(key)
        except Exception:
            return None
    
    async def set_binary(self, key: str, value: bytes, expire: int = 3600) -> bool:
        """Сохранить бинарные данные в кэш"""
        if not self.redis:
            return False
        try:
            await self.redis.setex(key, expire, value)
            return True
        except Exception as e:
            print(f"Binary cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        if not self.redis:
            return False
        try:
            await self.redis.delete(key)
            return True
        except Exception:
            return False


# Глобальный экземпляр бинарного кэша
binary_redis_cache = BinaryRedisCache()


def cache_image_binary(
        prefix: str = "image", expire: int = 3600,  # 1 час для изображений
        key_params: Optional[list] = None
        ):
    """
    Декоратор для кэширования бинарных данных изображений
    Работает с сервисами, возвращающими dict с полем 'content'
    """
    
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Формируем ключ кэша
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
            
            # Пытаемся получить бинарные данные из кэша
            cached_content = await binary_redis_cache.get_binary(cache_key)
            if cached_content is not None:
                # Возвращаем структуру с данными из кэша
                return {"content": cached_content, "filename": f"cached_{cache_key.split(':')[-1]}",
                        "content_type": "image/png",  # или определить из metadata
                        "from_cache": True}
            
            # Выполняем функцию, если данных нет в кэше
            result = await func(*args, **kwargs)
            
            # Сохраняем бинарные данные в кэш, если результат содержит content
            if (isinstance(result, dict) and "content" in result and isinstance(result["content"], bytes)):
                await binary_redis_cache.set_binary(cache_key, result["content"], expire)
                result["from_cache"] = False
            
            return result
        
        return wrapper
    
    return decorator

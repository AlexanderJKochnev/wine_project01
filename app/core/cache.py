import json
import functools
from typing import Any, Optional, Callable
from redis.asyncio import Redis
from app.core.config.project_config import settings
import inspect
from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel


class JSONEncoder(json.JSONEncoder):
    """Кастомный JSON энкодер для обработки специальных типов"""
    
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, BaseModel):
            # Используем model_dump(by_alias=True) для правильного сохранения алиасов
            return obj.model_dump(by_alias = True)
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return super().default(obj)


class RedisCache:
    def __init__(self):
        self.redis: Optional[Redis] = None
    
    async def init_redis(self):
        """Инициализация подключения к Redis"""
        self.redis = Redis(
                host = settings.REDIS_HOST, port = settings.REDIS_PORT, decode_responses = True,
                socket_connect_timeout = 5, socket_timeout = 5
                )
    
    async def close(self):
        """Закрытие подключения"""
        if self.redis:
            await self.redis.close()
    
    async def get(self, key: str) -> Any:
        """Получить данные из кэша"""
        if not self.redis:
            return None
        
        try:
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
        except Exception:
            return None
    
    async def set(self, key: str, value: Any, expire: int = 300) -> bool:
        """Сохранить данные в кэш"""
        if not self.redis:
            return False
        
        try:
            # Используем кастомный энкодер с поддержкой model_dump(by_alias=True)
            serialized_value = json.dumps(value, cls = JSONEncoder, ensure_ascii = False)
            await self.redis.setex(key, expire, serialized_value)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Удалить данные из кэша"""
        if not self.redis:
            return False
        
        try:
            await self.redis.delete(key)
            return True
        except Exception:
            return False
    
    async def delete_pattern(self, pattern: str) -> bool:
        """Удалить данные по паттерну"""
        if not self.redis:
            return False
        
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
            return True
        except Exception:
            return False


# Глобальный экземпляр кэша
redis_cache = RedisCache()


def cache_key_builder(
        prefix: str = "cache", expire: int = 300, key_params: Optional[list] = None
        ):
    """
    Декоратор для кэширования результатов функций
    """
    
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Формируем ключ кэша
            cache_key = f"{prefix}:{func.__module__}:{func.__name__}"
            
            # Добавляем параметры в ключ, если указаны
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
            
            # Пытаемся получить данные из кэша
            cached_result = await redis_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Выполняем функцию, если данных нет в кэше
            result = await func(*args, **kwargs)
            
            # Сохраняем результат в кэш только если он не None
            if result is not None:
                await redis_cache.set(cache_key, result, expire)
            
            return result
        
        return wrapper
    
    return decorator


def invalidate_cache(patterns: list[str]):
    """
    Декоратор для инвалидации кэша после выполнения функции
    """
    
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            # Инвалидируем кэш по паттернам
            for pattern in patterns:
                await redis_cache.delete_pattern(pattern)
            
            return result
        
        return wrapper
    
    return decorator

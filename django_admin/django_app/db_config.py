# django_admin/django_app/db_config.py
import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv


def get_path_to_root(name: str = '.env'):
    """
        get path to fiile in root directory
    """
    for k in range(5):
        env_path = Path(__file__).resolve().parents[k] / name
        if env_path.exists():
            break
    else:
        env_path = None
        raise Exception('environment file is not found')
    return env_path


# Загружаем переменные окружения
env_path = get_path_to_root()
# env_path = Path(__file__).resolve().parent.parent.parent
load_dotenv(env_path)


class ConfigDataBase:
    """Postgresql Database Settings"""

    def __init__(self):
        # Основные настройки базы данных
        self.POSTGRES_USER = os.getenv('POSTGRES_USER', '')
        self.POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')
        self.POSTGRES_HOST = os.getenv('POSTGRES_HOST', '')
        self.POSTGRES_PORT = os.getenv('POSTGRES_PORT', '')
        self.POSTGRES_DB = os.getenv('POSTGRES_DB', '')
        self.DB_ECHO_LOG = os.getenv('DB_ECHO_LOG', 'False').lower() == 'true'

        # Настройки аутентификации
        self.SECRET_KEY = os.getenv('SECRET_KEY', '')
        self.ALGORITHM = os.getenv('ALGORITHM', '')

        # Валидация обязательных полей
        self._validate_required_fields()

    def _validate_required_fields(self):
        """Проверяет наличие обязательных переменных окружения"""
        required_fields = ['POSTGRES_USER',
                           'POSTGRES_PASSWORD', 'POSTGRES_HOST', 'POSTGRES_PORT', 'POSTGRES_DB',
                           'SECRET_KEY', 'ALGORITHM']

        missing_fields = []
        for field in required_fields:
            if not getattr(self, field):
                missing_fields.append(field)

        if missing_fields:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_fields)}")

    @property
    def database_url(self) -> Optional[str]:
        """
        Возвращает строку подключения для asyncpg
        """
        return (f"postgresql+asyncpg://{self.POSTGRES_USER}:"
                f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
                f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}")

    @property
    def django_database_url(self) -> Optional[str]:
        """
        Возвращает строку подключения для Django
        """
        return (f"postgresql://{self.POSTGRES_USER}:"
                f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
                f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}")

    def to_dict(self) -> Dict[str, Any]:
        """Возвращает все настройки в виде словаря"""
        return {'POSTGRES_USER': self.POSTGRES_USER, 'POSTGRES_PASSWORD': self.POSTGRES_PASSWORD,
                'POSTGRES_HOST': self.POSTGRES_HOST, 'POSTGRES_PORT': self.POSTGRES_PORT,
                'POSTGRES_DB': self.POSTGRES_DB, 'DB_ECHO_LOG': self.DB_ECHO_LOG, 'SECRET_KEY': self.SECRET_KEY,
                'ALGORITHM': self.ALGORITHM, 'database_url': self.database_url,
                'django_database_url': self.django_database_url}


# Создаем экземпляр настроек
settings_db = ConfigDataBase()


def get_auth_data() -> Dict[str, str]:
    """Возвращает данные для аутентификации"""
    return {"secret_key": settings_db.SECRET_KEY, "algorithm": settings_db.ALGORITHM}


# Пример использования
if __name__ == "__main__":
    print("Database URL:", settings_db.database_url)
    print("Django Database URL:", settings_db.django_database_url)
    print("Auth data:", get_auth_data())

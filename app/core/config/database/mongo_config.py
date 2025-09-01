# app/core/config/database/mongo_confog.py
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.utils.common_utils import get_path_to_root


# load_dotenv() - не использовать - путает


class ConfigDataBase(BaseSettings):
    """ Postgresql Database Setting """
    model_config = SettingsConfigDict(env_file=get_path_to_root(),
                                      env_file_encoding='utf-8',
                                      extra='ignore')

    # MongoDB
    MONGODB_USER_NAME: str
    MONGODB_USER_PASSWORD: str
    MONGODB_DATABASE_AUTH_NAME: str
    MONGODB_REPLICA_SET: str
    MONGODB_REPLICA_SET_HOST: str  # ← Имя сервиса в docker-compose
    MONGODB_PORT: int
    MONGODB_DATABASE: str

    # probable secirity issue:
    SECRET_KEY: str
    ALGORITHM: str

    @property
    def mongodb_url(self) -> Optional[str]:
        """
        выводит строку подключения
        :return:
        :rtype:
        """
        return None


settings = ConfigDataBase()

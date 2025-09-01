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

    MONGO_DB_NAME: str      # myapp_mongodb
    MONGO_USER: str         # mongouser
    MONGO_PASSWORD: str     # mongopassword
    MONGO_HOST: str         # mongodb
    MONGO_PORT: int         # 27017
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
        return (
            f"mongodb://{self.MONGO_USER}:"
            f"{self.MONGO_PASSWORD}@{self.MONGO_HOST}:"
            f"{self.MONGO_PORT}/{self.MONGO_DB_NAME}"
            f"?authSource=admin"
        )


settings = ConfigDataBase()

# streamlit_app/config/project_config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


def get_path_to_root(name: str = '.env'):
    """
        get path to file or directory in root directory
    """
    for k in range(1, 10):
        env_path = Path(__file__).resolve().parents[k] / name
        if env_path.exists():
            break
    else:
        env_path = None
        raise Exception('environment file is not found')
    return env_path


class Settings(BaseSettings):
    """ Project Settings """
    POSTGRES_HOST: str = 'wine_host'
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = 'wine_db'
    POSTGRES_USER: str = 'wine'
    POSTGRES_PASSWORD: str = 'wine1'
    MONGO_HOSTNAME: str = 'mongodb'  # MONGO_HOST
    MONGO_OUT_PORT: int = 27017      # MONGO_PORT
    MONGO_INITDB_ROOT_USERNAME: str = 'admin'  # MONGO_USER
    MONGO_INITDB_ROOT_PASSWORD: str = 'admin'  # MONGO_PASSWORD
    BASE_URL: str = 'http://83.167.126.4'
    PORT: int = 18091
    # FASTAPI_URL = f'{BASE_URL}:{PORT}'

    model_config = SettingsConfigDict(env_file=get_path_to_root(),
                                      env_file_encoding='utf-8',
                                      extra='ignore')

    @property
    def MONGO_USER(self) -> str:
        return self.MONGO_INITDB_ROOT_USERNAME

    @property
    def MONGO_PASSWORD(self) -> str:
        return self.MONGO_INITDB_ROOT_PASSWORD

    @property
    def MONGO_HOST(self) -> str:
        return self.MONGO_HOSTNAME

    @property
    def MONGO_PORT(self) -> int:
        return self.MONGO_OUT_PORT

    @property
    def FASTAPI_URL(self) -> str:
        return f'{self.BASE_URL}:{self.PORT}'


settings = Settings()

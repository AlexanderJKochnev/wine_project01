# tests/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="tests/.env.tests",
                                      env_file_encoding='utf-8',
                                      extra='ignore')
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: int
    PG_PORT: int
    POSTGRES_HOST: str
    DB_ECHO_LOG: int

    MONGODB_USER_NAME: str
    MONGODB_USER_PASSWORD: str
    MONGODB_DATABASE_AUTH_NAME: str
    MONGODB_REPLICA_SET: str
    MONGODB_REPLICA_SET_HOST: str  # ← Имя сервиса в docker-compose
    MONGODB_PORT: str
    MONGODB_DATABASE: str

    @property
    def mogodb_url(self):
        return (f'mongodb://'
                f'{self.MONGODB_USER_NAME}:'
                f'{self.MONGODB_USER_PASSWORD}@'
                f'{self.MONGODB_REPLICA_SET_HOST}:'
                f'{self.MONGODB_PORT}/'
                f'{self.MONGODB_DATABASE}?authSource=admin')


settings = Settings()


# внешний url
base_url_out: str = 'http://83.167.126.4:18091/'

# локальный url в docker
base_url_doc: str = 'http://localhost:8091/'

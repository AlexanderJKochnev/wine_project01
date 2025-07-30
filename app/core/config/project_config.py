# app/core/config/project_config.py
# from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# load_dotenv()


class Settings(BaseSettings):
    """ Project Settings """
    DB_ECHO: bool
    PROJECT_NAME: str
    VERSION: str
    DEBUG: bool
    CORS_ALLOWED_ORIGINS: str

    class Config:
        env_file = ".env"


settings = Settings()

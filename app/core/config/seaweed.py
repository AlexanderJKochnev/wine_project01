# app/core/config/databse/file.py
from aiobotocore.session import get_session
# from botocore.exceptions import ClientError
from pydantic_settings import BaseSettings, SettingsConfigDict
from contextlib import asynccontextmanager
from app.core.utils import get_path_to_root


class ConfigSeaweedBase(BaseSettings):
    """ Postgresql Database Setting """
    model_config = SettingsConfigDict(env_file=get_path_to_root(),
                                      env_file_encoding='utf-8',
                                      extra='ignore')
    SEAWEED_MASTER_PORT: int
    SEAWEED_S3_PORT: int
    SEAWEED_VOLUME_PORT: int
    SEAWEED_URL: str
    AWS_ACCESS_KEY_ID: str = 'any'
    AWS_SECRET_ACCESS_KEY: str = 'any'
    REGION_NAME: str = "us-east-1"
    SEAWEED_BUCKET_NAME: str = 'uploads'

    @property
    def endpoint_url(self) -> str:
        # return "http://seaweedfs:8888"
        return f'{self.SEAWEED_URL}:{self.SEAWEED_S3_PORT}'

    @property
    def filer_uploads_url(self) -> str:
        return f"{self.SEAWEED_URL}:{self.SEAWEED_S3_PORT}/{self.SEAWEED_BUCKET_NAME}"


setting_seaweed = ConfigSeaweedBase()


@asynccontextmanager
async def get_s3_client():
    print("S3 endpoint URL:", setting_seaweed.endpoint_url)
    session = get_session()
    async with session.create_client("s3",
                                     endpoint_url=setting_seaweed.endpoint_url,
                                     aws_access_key_id=setting_seaweed.AWS_ACCESS_KEY_ID,
                                     aws_secret_access_key=setting_seaweed.AWS_SECRET_ACCESS_KEY,
                                     region_name=setting_seaweed.REGION_NAME) as client:
        yield client

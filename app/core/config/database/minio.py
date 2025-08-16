# app/core/config/database/minio.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from minio import Minio
# from minio.error import S3Error
from app.core.utils import get_path_to_root


class ConfigMinioBase(BaseSettings):
    """ Postgresql Database Setting """
    model_config = SettingsConfigDict(env_file=get_path_to_root(),
                                      env_file_encoding='utf-8',
                                      extra='ignore')
    MINIO_URL: str
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    # MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str
    MINIO_SECURE: str = False


setting_minio = ConfigMinioBase()

# Создаём клиент MINIO_URL SHALL BE WITHOUT http://... prefixes
minio_client = Minio(setting_minio.MINIO_URL.removeprefix("https://").removeprefix("http://"),
                     access_key=setting_minio.MINIO_ROOT_USER,
                     secret_key=setting_minio.MINIO_ROOT_PASSWORD,
                     secure=False)  # False для localhost без HTTPS


bucket_name = setting_minio.MINIO_BUCKET


# Проверяем/создаём бакет
def initialize_minio():
    try:
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' created successfully.")
        # Опционально: устанавливаем политику публичного доступа
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": ["s3:GetObject"],
                    "Resource": f"arn:aws:s3:::{bucket_name}/*"
                }
            ]
        }
        minio_client.set_bucket_policy(bucket_name, str(policy).replace("'", '"'))
        print(f"Bucket '{bucket_name}' is now public.")
    except Exception as e:
        print(f"MinIO initialization error: {e}")


initialize_minio()

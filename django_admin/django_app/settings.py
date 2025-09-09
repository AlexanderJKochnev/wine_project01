# django_admin/django_app/settings.py
from pathlib import Path
import sys

# Получаем корневую директорию
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))
print(f'{root_dir=}')
from django_app.db_config import settings_db  # noqa: E402

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-fastapi-django-integration'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # для i18n
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'django_app.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': settings_db.POSTGRES_DB,  # os.getenv('POSTGRES_DB'),
        'USER': settings_db.POSTGRES_USER,  # os.getenv('POSTGRES_USER'),
        'PASSWORD': settings_db.POSTGRES_PASSWORD,  # os.getenv('POSTGRES_PASSWORD'),
        'HOST': settings_db.POSTGRES_HOST,  # 'postgres',
        'PORT': settings_db.POSTGRES_PORT  # '5432',
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'django_app.wsgi.application'
AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = 'ru'
LANGUAGES = [
    ('en', 'English'),
    ('ru', 'Русский'),
]
LOCALE_PATHS = [BASE_DIR / "locale"]
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
MEDIA_URL = '/media/'
MEDIA_ROOT = '/app/media'
STATIC_ROOT = '/app/staticfiles'
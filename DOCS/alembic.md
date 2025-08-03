# НАСТРОЙКА ALEMBIC #
1. Запуск из app
2. alembic init -t async migration
   1. migration: название директории с миграциями
3. alembic.ini
   1. заменить параметр sqlalchemy.url = postgresql+asyncpg://<user>:<password>@<host>:<port>/<db>
      1. user = .env/POSTGRES_USER
      2. password = .env/POSTGRES_PASSWORD
      3. host = .env/POSTGRES_HOST
      4. port = .env/POSTGRES_PORT
      5. db = .env/POSTGRES_DB
      6. пример: sqlalchemy.url = postgresql+asyncpg://wine:wine1@wine_host:5432/wine_db
   2. script_location = заменить migration -> app/migration 
4. migration/env.py:
   1. После 'from alembic import context' вставить все что ниже:
   2. import sys 
   3. from os.path import dirname, abspath
   4. sys.path.insert(0, dirname(dirname(abspath(__file__))))
   5. from src.models.base_model import Base  # noqa: F401, E402 ## нужно добавить все модели включая базовую
   6. from src.models.user_model import UserModel   # noqa: F401, E402  ## порядок имеет значение, сначала Base, 
   7. from src.models.category_model import CategoryModel ## затем модели на которые есть ссылки foreign key
   8. from src.config.database.db_config import settings_db ## затем остальные 
   9. config = context.config   уже есть
   10. section = config.config_ini_section  # эти строки нужно добавить после config = context.config 
   11. config.set_section_option(section, "POSTGRES_HOST", settings_db.POSTGRES_HOST)
   12. config.set_section_option(section, "POSTGRES_PORT", settings_db.POSTGRES_PORT)
   13. config.set_section_option(section, "POSTGRES_USER", settings_db.POSTGRES_USER)
   14. config.set_section_option(section, "POSTGRES_DB", settings_db.POSTGRES_DB)
   15. config.set_section_option(section, "POSTGRES_PASSWORD",
                           settings_db.POSTGRES_PASSWORD)
   16. if config.config_file_name is not None:
   17. fileConfig(config.config_file_name)
   18. target_metadata = Base.metadata
5. перенести alembic.ini из app в корень
6. После запуска приложения в docker, запустить из командной строки:
   1. sh alembic.sh (он выполгнит следующие команды и выполнит миграцию изменений в бд)
      1. docker compose exec app alembic revision --autogenerate -m 'Initial revision'
      2. docker compose exec app alembic upgrade head

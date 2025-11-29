# tests/test_configs.py
# тестирование конфигурационных файлов


def test_config_postgres():
    try:
        from app.core.config.database.db_config import settings_db  # noqa: F401
        from app.core.config.project_config import settings  # noqa: F401
        assert True
    except Exception as e:
        assert False, f'ошибка в конфигурационных файлах {e}'

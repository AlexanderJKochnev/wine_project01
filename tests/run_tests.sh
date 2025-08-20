#!/bin/bash

# тесты снаружи контейнера
# pytest --ignore=tests/test_postgres.py --ignore=tests/test_mock_db.py --tb=no --disable-warnings -vv
# pytest tests/ --ignore=tests/test_postgres.py --tb=no --disable-warnings -vv
# docker exec -it app pytest tests/test_postgres.py --tb=no --disable-warnings -vv
pytest tests/test_color_crud.py tests/test_sqladmin.py tests/test_fastapi.py tests/test_database.py tests/test_database_connection.py --tb=auto --disable-warnings -vv --capture=no

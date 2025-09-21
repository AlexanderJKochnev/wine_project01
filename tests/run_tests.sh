#!/bin/bash

# тесты снаружи контейнера
# pytest --ignore=tests/test_postgres.py --ignore=tests/test_mock_db.py --tb=no --disable-warnings -vv
# pytest tests/ --ignore=tests/test_postgres.py --tb=no --disable-warnings -vv
# docker exec -it app pytest tests/test_postgres.py --tb=no --disable-warnings -vv
# pytest tests/test_sqladmin.py tests/test_fastapi.py tests/test_database.py tests/test_database_connection.py --tb=auto --disable-warnings -vv --capture=no
# pytest -m 'not docker' --tb=no --disable-warnings -vv
pytest tests/test_auth.py \
       tests/test_configs.py \
       tests/test_database.py \
       tests/test_database_connection.py \
       tests/test_fastapi.py \
       tests/test_create.py \
       tests/test_get.py \
       tests/test_search.py \
       tests/test_update.py \
       tests/test_mongodb.py
       # tests/test_delete.py --tb=auto --log-cli-level=WARNING
       # search patch - проверить и вылечить

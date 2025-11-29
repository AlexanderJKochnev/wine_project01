#!/bin/bash

# тесты снаружи контейнера
# pytest --ignore=tests/test_postgres.py --ignore=tests/test_mock_db.py --tb=no --disable-warnings -vv
# pytest tests/ --ignore=tests/test_postgres.py --tb=no --disable-warnings -vv
# docker exec -it app pytest tests/test_postgres.py --tb=no --disable-warnings -vv
# pytest -m 'not docker' --tb=no --disable-warnings -vv
pytest tests/test_mongodb_crud.py
pytest tests/test_mongodb_endpoints.py
pytest tests/test_mongodb.py
pytest tests/test_create_mongo.py
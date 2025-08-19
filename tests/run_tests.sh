#!/bin/bash

# тесты снаружи контейнера
# pytest tests/test_fastapi.py --ignore=tests/test_postgres.py --tb=no --disable-warnings -vv
pytest tests/ --ignore=tests/test_postgres.py --tb=no --disable-warnings -vv
# docker exec -it app pytest tests/test_postgres.py --tb=no --disable-warnings -vv
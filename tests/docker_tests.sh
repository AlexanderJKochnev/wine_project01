#!/bin/bash

# тесты внутри запещенного контейнера

docker exec -it app pytest tests/test_postgres.py --tb=no --disable-warnings -vv
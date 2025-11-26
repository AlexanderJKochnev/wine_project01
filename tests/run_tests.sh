#!/bin/bash

# test_create.py запускать отдельно - разобраться почему падает в группе
# pytest tests/test_create.py

pytest tests/test_mongodb_integral.py
pytest tests/test_mongodb_endpoints.py
pytest tests/test_auth.py \
       tests/test_configs.py \
       tests/test_database.py \
       tests/test_database_connection.py \
       tests/test_fastapi.py
pytest tests/test_get.py \
       tests/test_update.py \
       tests/test_search.py \
       tests/test_preact.py \
       tests/test_mongodb.py \
       tests/test_delete.py
pytest tests/test_create_mongo.py
pytest tests/test_converter.py

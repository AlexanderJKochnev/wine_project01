#!/bin/bash

# тесты снаружи контейнера

pytest --cov=app --cov-report=term-missing tests/ tests/ --ignore=tests/test_postgres.py
pytest --cov=app --cov-report=html tests/ --ignore=tests/test_postgres.py
open htmlcov/index.html
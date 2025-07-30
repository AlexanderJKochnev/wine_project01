#!/bin/bash


# echo -e "\n введите путь к директории:"
# read path_to
mkdir -p tests
touch .env
mkdir -p app/support/template
mkdir -p app/core/config/database
mkdir -p app/core/models
mkdir -p app/core/repositories
mkdir -p app/core/schemas
mkdir -p app/core/services
cd app/support/template
touch  __init__.py models.py repository.py router.py schemas.py service.py
cd ..
# app/support/
touch __init__.py
cd ..
# app/
touch __init__py main.py depends.py exceptions.py
cd core/config/database
# app/core/config/database
touch __init__.py db_config.py db_helper.py db_noclass.py
cd ..
# app/core/config
touch __init__.py project_config.py
cd ../models
# app/core/models
touch __init__.py base_model.py
cd ../repositories
# app/core/repositories
touch __init__.py base_repository.py mongo_repository.py sqlalchemy_repository.py
cd ../schemas
# app/core/schemas
touch __init__.py base_schema.py
cd ../services
# app/core/services
touch __init__.py base_service.py query_base_service.py
cd ..
# app/core
touch __init__.py
cd ../..
# root
touch docker-compose.yaml Dockerfile .env
touch .gitignore .dockerignore

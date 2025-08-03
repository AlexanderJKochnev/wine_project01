# FastAPI не поддерживает Python 3.13 (август 2025)

1. COMMON SCHEME OF THIS FASTAPI APPLICATION 
   1. HTTP REQUEST:
   2. ROUTING
   3. SERVICES
   4. REPOSITORIES
   5. DATABASE

FILE SYSTEM HIERARCHY
- app
  - core: настройки, шаблоны, 
    - config: конфигурация
      - databases: конфигурация баз данных
        - pgsql
        - mongodb.py
      - project_config.py: конфигурация проекта
    - routing: марщрутизация
    - schemas: шаблоны схем передачи данных между слоями (DTO data transfer objects)
    - services: бизнес логика
    - repositories: шаблоны взаимодействия с базой данных
    - models: модели таблиц базы данных
  - support:
- tests: тестирование

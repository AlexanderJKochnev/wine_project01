# FastAPI не поддерживает Python 3.13 (август 2025)

1. COMMON SCHEME OF THIS FASTAPI APPLICATION 
   1. HTTP REQUEST 
   2. ROUTING:  FastAp
   3. SERVICES: функции которые принимают аргументом repository, а возвращают отформатированный результат by schema
   4. REPOSITORIES: модели запроса (классы, описывающие тело запроса)
   5. SCHEMAS: модели ответа Pydantic (которые возвращает роутер (заполненные)
   6. DATABASE

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

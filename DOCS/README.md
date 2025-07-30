 # документы по темам см /docs/
1. создание скелета fastapi приложения (запуск из корня)
   1. sh scripts/struct_ini.sh
2. Заполнение скелета данными 
   1. заполнить/скопировать директории app/core
3. запуск alembic (DOCS/alembic.md)
4. Создание сущностей (таблиц данных для postgresql и все что нужно для их обслуживания)
   1. см. DOCS/rightway.md
5. uvicorn app.main:app --reload или fastapi run | fastapi dev
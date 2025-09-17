# app/support/template/README.md
1. Определись с названием сущности исходя из следующих критериев:
   1. Название должно отражать суть (таблица государств - State) и состоять из одного слова только из букв англ алфавита
   2. Наименование класса с большой буквы в ед. числе.  (желательно не входит в список зарезервированных слов)
2. Создай директорию в app/support/<название сущности>
3. Скопируй туда полностью содержимое директории любой директории из app/support/ подходящее по структуре и далее редактируй:
   1. model.py
   2. repository
   3. router
   4. schemas
   5. service
   6. app.main.py (import, app.include.router())
   7. app.migration.env.py (import)
   8. в model.py найти в полях relationships связанные модели (both child & parent) и пройтись по их директориях
      1. model.py
      2. repository get_query!!!
      3. schemas.py
      4. service.py !!!
   9. tests/conftest.py (import ...)
   10. django_admin
       1. django_admin/apps/core/models.py
       2. django_admin/apps/core/admin.py

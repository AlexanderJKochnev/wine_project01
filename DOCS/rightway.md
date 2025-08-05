## Добавление новой сущности в проект.
1. Скопировать папку app.support.template в app.support.<name>
   1. name: наименование 
      1. в ед.числе 
      2. в нижнем регистре 
      3. без пробелов и любых других знаков кроме букв и чисел
      4. на первом месте только буквы
2. Заполнить данными файлы в созданой директории в следующем порядке:
   1. models.py
      1. добавить созданную модель в migration/env.py секция import
      2. alembic revision --autogenerate -m "<name> revision" -> потом при перезапруске docker
      3. alembic upgrade head -> потом при перезапруске docker
   2. service.py
   3. schemas.py
      1. Hint: S<name> = S<name>Add + id: int
   4. repository.py
   5. router.py
   6. add/main.py (добавить новый роутер)
3. Добавить роутер в SQLAdmin:
   1. app/admin/sqladmin.py добавить класс по аналогии с имеющимися
   2. app/main.py доавить роутер admin.add_view(sqladm.<Name>Admin)
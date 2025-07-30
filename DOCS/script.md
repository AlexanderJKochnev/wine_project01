# DOCS/script.md
Описание скрипта для создания структуры сущности:
1. Исходные данные:
   1. Имя сущности ('_Name, Surname')
   2. База данных для хранения сущности ?
2. Подготовка данных:
   1. '_Name, surname' -> 'NameSurname' (только буквы и цифры, ед.ч.) для классов
   2. 'NameSurname' -> 'namesurnames' (lowest, plural) для директорий/таблиц в database
   3. Проверка на уникальность, если уже есть -> остановка
3. Создание скелета на основе src/support/template:
   1. создание директрории: mkdir /src/support/namessurnames
   2. cd /src/support/namessurnames
   3. копирование содержимого templates в директорию scp /src/support/template/* /src/support/<namessurnames>
4. Изменения в файлах:
   1. src/support/<namesurnames>/models.py: 
      1. TemplateModel ->  <NameSurname>Model
   2. src/support/<namesurnames>/schemas.py: 
      1. Template* -> <NameSurname>*
   3. src/support/<namesurnames>/router.py: 
      1. Template* -> <NameSurname>*
      2. template -> <namessurnames>
      3. short_notice -> customized notice
   4. migration/env.py добавить в конец секции импорта:
      1. from src.support.<namesurnames>.models import <NameSurname>Model   # noqa: F401
   5. src/main.py добавить 
      1. в конец секции импорта:
         1. from src.support.<namesurnames>.router import router as <namesurnames>_router
      2. после последней строки app.include_router...  добавить строку :
         1. app.include_router(<namesurnames>_router)
   6. 
5. 
Перенос базы данных:
2. sh sqldump.sh
   1. copy backup
   scp -r myt:/home/alexander/dockers/wine/pg_dump/backup.dump /Users/kochnev/PycharmProjects/wine/wine_project02/pg_dump/
2. sh restore.sh
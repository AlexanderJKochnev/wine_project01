# полключение совего git repository
## посмотреть настройки уже существующего репо
git remote -v
## создать на сервере пустой репо
mkdir new_project.git
cd new_project.git
git init --bare

## на локальном компьютере
git remote add local mydebby:/home/alex/nginx.git
git push local main
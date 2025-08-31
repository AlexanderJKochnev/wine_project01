1. инициализация
echo "# wine_project01" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/AlexanderJKochnev/wine_project01.git
git push -u origin main

2. git status
3. git add .
4. git commit -m "описание commit"
5. git push -u origin main

linux - на этой стороне ничего не менять
1. ssh-keygen -t ed25519 -C "ваш_email@example.com"
2. eval "$(ssh-agent -s)"  # Запуск ssh-agent
3. ssh-add ~/.ssh/id_ed25519  # Добавление ключа
4. cat ~/.ssh/id_ed25519.pub
5. cкопировать вывод ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJd7... ваш_email@example.com 
6. на сайте github Перейдите в Settings → SSH and GPG keys → New SSH key. 
7. Вставьте скопированный ключ. 
8. Нажмите Add SSH key.
9. Проверка подключения ssh -T git@github.com
10. git config --global url."git@github.com:".insteadOf "https://github.com/"
11. git clone git@github.com:username/repo.git
12. git branch -M main  # Убедитесь, что локальная ветка имеет правильное имя 
13. git pull origin main  # Обновите её из удалённого репозитория
14. если ветка поменалась
    1. git switch -c master
    2. git fetch origin
    3. git checkout master
    4. git pull origin master
    5. git reset hard (если попросит stash)

как клонировать в новую папку с активной venv & git
1. git remote add origin https://github.com/AlexanderJKochnev/wine_project01.git
2. rm -r .idea
3. git pull origin main

 описание последнего коммита
 git log -1
 
откат до последнего коммита
git reset --hard HEAD

слияние двух веток (просто, но много мусора)
1. merge
    git checkout <branche_1>
    git merge <branche_2>
    сольется в branche_1

2. rebase Этот способ "перемещает" коммиты одной ветки <branche_2> на верх другой <branche_1>, создавая линейную историю.
    git checkout <branche_2>
    git rebase <branche_1>
    сольется в branche_1
    Если есть конфликты, разрешите их, затем выполните:
    git add .
    git rebase --continue
    после перебазирования сделать rebase
    git checkout <branche_1>
    git merge <branche_2>

# Забрать все обновления с удалённого репозитория (включая новые ветки)
git fetch origin
# Посмотреть, какие ветки доступны
git branch -a
# Переключиться напрямую (Git 2.23+)
git switch mongo
# Использовать checkout
git checkout mongo

# Посмотреть какие неотслеживаниемые фалы будут удалены
git clean -fdn
# Удалить неотслеживаемые файлы
git clean -fd

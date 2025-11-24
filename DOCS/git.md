# DOCS/git.md
##  слияние веток:
git checkout main
git pull origin main
git merge tmp

## удаление ветки после слияния
удаление локальной ветки оставшейся после слияния (еслит слияние не прошло - ничего не удалится)
git branch -d <имя_ветки>
удаление удаленной (remote) ветки после локальной
git push origin --delete <имя_ветки>
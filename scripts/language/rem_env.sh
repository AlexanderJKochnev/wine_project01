#!/bin/bash

# Script to remove a language code to the LANGSS variable in .env file

# Check if argument is provided
if [ $# -ne 1 ]; then
    echo "Error: Please provide a two-letter language code as an argument"
    exit 1
fi

arg="$1"

# Validate the argument (2 letters of Latin alphabet)
if [[ ! "$arg" =~ ^[a-zA-Z]{2}$ ]]; then
    echo "Error: Argument must be a two-letter Latin alphabet code"
    exit 1
fi

# Convert to lowercase
DEL_VAL=$(echo "$arg" | tr '[:upper:]' '[:lower:]')

GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
ENV_FILE="$GIT_ROOT/.env"

if [ -f "$ENV_FILE" ]; then
    # 1. Извлекаем текущее значение и убираем пробелы
    CURRENT_VAL=$(grep "^LANGS=" "$ENV_FILE" | cut -d '=' -f2- | xargs)

    # 2. Проверяем, есть ли что удалять
    if [[ ",$CURRENT_VAL," == *",$DEL_VAL,"* ]]; then
        
        # 3. Хитрость удаления: 
        # Добавляем запятые по краям, удаляем ",es,", затем убираем лишние запятые по краям
        NEW_VAL=$(echo ",$CURRENT_VAL," | sed "s/,$DEL_VAL,/,/g" | sed 's/^,//;s/,$//')
        
        # Если после удаления остались двойные запятые (было "en,es,ru" -> "en,,ru")
        NEW_VAL=$(echo "$NEW_VAL" | sed 's/,,/,/g')

        # 4. Записываем обратно в файл (синтаксис macOS)
        sed -i '' "s|^LANGS=.*|LANGS=$NEW_VAL|" "$ENV_FILE"
        echo "Значение '$DEL_VAL' удалено. Новое значение: LANGS=$NEW_VAL"
    else
        echo "Значение '$DEL_VAL' не найдено в строке: $CURRENT_VAL"
    fi
else
    echo "Файл .env не найден"
fi
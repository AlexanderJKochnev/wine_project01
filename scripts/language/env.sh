#!/bin/bash

# Script to add a language code to the LANGS variable in .env file

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
ADD_VAL=$(echo "$arg" | tr '[:upper:]' '[:lower:]')

GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
ENV_FILE="$GIT_ROOT/.env"

if [ -f "$ENV_FILE" ]; then
    # 1. Читаем значение LANGS, убираем пробелы по краям
    CURRENT_VAL=$(grep "^LANGS=" "$ENV_FILE" | cut -d '=' -f2- | xargs)

    # 2. Проверяем, есть ли уже значение в списке
    # Окружаем запятыми для точного поиска, чтобы 'es' не нашелся в 'estonia'
    if [[ ",$CURRENT_VAL," == *",$ADD_VAL,"* ]]; then
        echo "Значение '$ADD_VAL' уже есть в списке: $CURRENT_VAL"
    else
        # 3. Формируем новую строку
        if [ -z "$CURRENT_VAL" ]; then
            NEW_VAL="$ADD_VAL"
        else
            NEW_VAL="$CURRENT_VAL,$ADD_VAL"
        fi

        # 4. Записываем в файл (синтаксис macOS)
        sed -i '' "s|^LANGS=.*|LANGS=$NEW_VAL|" "$ENV_FILE"
        echo "Добавлено. Новое значение: LANGS=$NEW_VAL"
    fi
else
    echo "Файл .env не найден"
fi
#!/usr/bin/env python3
"""
Скрипт для удаления языкового кода из приложения.
Удаляет соответствующие поля из моделей, схем, фронтенда и других компонентов.
"""
import os
import re
import sys
import argparse
from pathlib import Path
from typing import List


def validate_language_code(lang_code: str) -> bool:
    """Проверяет, является ли код языка допустимым (2 буквы латинского алфавита)"""
    return bool(re.match(r'^[a-z]{2}$', lang_code.lower()))


def get_current_languages_from_env(env_path: str) -> List[str]:
    """Получает текущий список языков из .env файла"""
    if not os.path.exists(env_path):
        raise FileNotFoundError(f"Файл .env не найден: {env_path}")
    
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Находим строку LANGS=...
    match = re.search(r'^LANGS\s*=\s*(.*)$', content, re.MULTILINE)
    if not match:
        raise ValueError("Не найдена переменная LANGS в .env файле")
    
    langs_str = match.group(1).strip()
    langs = [lang.strip() for lang in langs_str.split(',') if lang.strip()]
    return langs


def remove_language_from_env(env_path: str, lang_code: str) -> bool:
    """Удаляет код языка из переменной LANGS в .env файле"""
    current_langs = get_current_languages_from_env(env_path)
    
    if lang_code not in current_langs:
        print(f"Язык '{lang_code}' не найден в списке: {', '.join(current_langs)}")
        return False
    
    current_langs.remove(lang_code)
    new_langs_str = ','.join(current_langs)
    
    # Обновляем .env файл
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = re.sub(r'^LANGS\s*=.*$', f'LANGS={new_langs_str}', content, flags=re.MULTILINE)
    
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Язык '{lang_code}' удален из .env. Новое значение: LANGS={new_langs_str}")
    return True


def remove_language_from_models(lang_code: str):
    """Удаляет языковые поля из моделей SQLAlchemy"""
    model_file = Path("/workspace/app/core/models/base_model.py")
    
    if not model_file.exists():
        print(f"Файл модели не найден: {model_file}")
        return
    
    with open(model_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Удаляем поля с использованием меток
    pattern = f"    # START_LANG_FIELD_{lang_code.upper()}.*?    # END_LANG_FIELD_{lang_code.upper()}\\n"
    content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # Обновляем метод __str__ в BaseFullFree
    # Удаляем упоминание языка из возвращаемого выражения
    base_full_free_start = content.find("class BaseFullFree")
    if base_full_free_start != -1:
        str_method_start = content.find("def __str__(self)", base_full_free_start)
        if str_method_start != -1:
            body_start = content.find("return", str_method_start)
            if body_start != -1:
                line_end = content.find("\n", body_start)
                if line_end != -1:
                    current_return = content[body_start:line_end].strip()
                    
                    # Удаляем упоминание языка из выражения
                    updated_return = current_return.replace(f" or self.name_{lang_code}", "")
                    updated_return = updated_return.replace(f"self.name_{lang_code} or ", "")
                    updated_return = updated_return.replace(f"self.name_{lang_code}", "")
                    
                    content = content[:body_start] + updated_return + content[line_end:]
    
    with open(model_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Языковые поля для '{lang_code}' удалены из моделей SQLAlchemy")


def remove_language_from_schemas(lang_code: str):
    """Удаляет языковые поля из Pydantic схем"""
    schema_file = Path("/workspace/app/core/schemas/base.py")
    
    if not schema_file.exists():
        print(f"Файл схемы не найден: {schema_file}")
        return
    
    with open(schema_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Удаляем поля с использованием меток
    pattern = f"    # START_LANG_FIELD_{lang_code.upper()}.*?    # END_LANG_FIELD_{lang_code.upper()}\\n"
    content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    with open(schema_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Языковые поля для '{lang_code}' удалены из Pydantic схем")


def remove_language_from_api_mixin(lang_code: str):
    """Удаляет языковые поля из API mixin"""
    mixin_file = Path("/workspace/app/core/schemas/api_mixin.py")
    
    if not mixin_file.exists():
        print(f"Файл api_mixin не найден: {mixin_file}")
        return
    
    with open(mixin_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Удаляем свойство для конкретного языка
    pattern = f"\n    @computed_field\n    @property\n    def name_{lang_code}\(self\) -> str:.*?\n        return self\.__get_lang__\('_{lang_code}'\)\n"
    content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    with open(mixin_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Языковое поле для '{lang_code}' удалено из API mixin")


def remove_language_from_lang_schemas(lang_code: str):
    """Удаляет языковые схемы для указанного языка"""
    lang_schema_file = Path("/workspace/app/core/schemas/lang_schemas.py")
    
    if not lang_schema_file.exists():
        print(f"Файл lang_schemas не найден: {lang_schema_file}")
        return
    
    with open(lang_schema_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Удаляем схемы с использованием меток
    pattern = f"# START_LANG_SCHEMA_{lang_code.upper()}.*?# END_LANG_SCHEMA_{lang_code.upper()}\n"
    content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    with open(lang_schema_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Языковые схемы для '{lang_code}' удалены")


def remove_language_from_translation_utils(lang_code: str):
    """Удаляет поддержку языка из утилит перевода"""
    translation_file = Path("/workspace/app/core/utils/translation_utils.py")
    
    if not translation_file.exists():
        print(f"Файл translation_utils не найден: {translation_file}")
        return
    
    with open(translation_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Удаляем упоминания языка из списка локализованных полей
    content = content.replace(f"'name_{lang_code}',", "")
    content = content.replace(f"'description_{lang_code}',", "")
    content = content.replace(f"'title_{lang_code}',", "")
    content = content.replace(f"'subtitle_{lang_code}',", "")
    
    # Удаляем из функции get_field_language
    pattern = f"    elif field_name.endswith\('_{lang_code}'\):\n        return '{lang_code}'\n"
    content = re.sub(pattern, '', content)
    
    # Удаляем из функции get_base_field_name
    content = content.replace(f"_{lang_code}',", "")
    content = content.replace(f"_{lang_code}')", "")
    
    with open(translation_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Поддержка языка '{lang_code}' удалена из утилит перевода")


def remove_language_from_frontend_types(lang_code: str):
    """Удаляет языковые поля из TypeScript типов"""
    types_file = Path("/workspace/preact_front/src/types/base.ts")
    
    if not types_file.exists():
        print(f"Файл TypeScript типов не найден: {types_file}")
        return
    
    with open(types_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Удаляем поля с использованием меток
    pattern = f"  // START_LANG_FIELD_{lang_code.upper()}.*?  // END_LANG_FIELD_{lang_code.upper()}\n"
    content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    with open(types_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Языковые поля для '{lang_code}' удалены из TypeScript типов")


def remove_language_from_frontend_forms(lang_code: str):
    """Удаляет языковые поля из форм фронтенда"""
    # Обновляем формы создания и обновления
    form_files = [
        Path("/workspace/preact_front/src/pages/ItemCreateForm.tsx"),
        Path("/workspace/preact_front/src/pages/ItemUpdateForm.tsx"),
        Path("/workspace/preact_front/src/pages/HandbookCreateForm.tsx"),
        Path("/workspace/preact_front/src/pages/HandbookUpdateForm.tsx")
    ]
    
    for form_file in form_files:
        if not form_file.exists():
            continue
        
        with open(form_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Удаляем поля из начального состояния
        content = content.replace(f"    title_{lang_code}: '',\n", "")
        content = content.replace(f"    subtitle_{lang_code}: '',\n", "")
        content = content.replace(f"    description_{lang_code}: '',\n", "")
        
        # Удаляем input элементы
        # Паттерн для удаления целого input блока
        pattern = rf'                  <input\s+type="text"\s+name="title_{lang_code}"[^>]*>.*?</input>\s*'
        content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        pattern = rf'                  <input\s+type="text"\s+name="subtitle_{lang_code}"[^>]*>.*?</input>\s*'
        content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        pattern = rf'                  <input\s+type="text"\s+name="description_{lang_code}"[^>]*>.*?</input>\s*'
        content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        # Также удаляем более простые паттерны
        content = re.sub(rf'\s*name="title_{lang_code}"[^}]*value={{formData\.title_{lang_code}}}[^>]*>\s*', '', content)
        content = re.sub(rf'\s*name="subtitle_{lang_code}"[^}]*value={{formData\.subtitle_{lang_code}}}[^>]*>\s*', '', content)
        content = re.sub(rf'\s*name="description_{lang_code}"[^}]*value={{formData\.description_{lang_code}}}[^>]*>\s*', '', content)
        
        with open(form_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f"Языковые поля для '{lang_code}' удалены из форм фронтенда")


def main():
    parser = argparse.ArgumentParser(description='Удалить языковой код из приложения')
    parser.add_argument('lang_code', help='Двухбуквенный код языка (например, de, es, it)')
    
    args = parser.parse_args()
    
    lang_code = args.lang_code.lower()
    
    # Проверяем код языка
    if not validate_language_code(lang_code):
        print(f"Ошибка: '{lang_code}' не является допустимым двухбуквенным кодом языка")
        sys.exit(1)
    
    if lang_code == 'en':
        print("Ошибка: Нельзя удалить английский язык (en), он используется по умолчанию")
        sys.exit(1)
    
    # Проверяем, есть ли такой язык в .env
    env_path = "/workspace/.env"
    current_langs = get_current_languages_from_env(env_path)
    
    if lang_code not in current_langs:
        print(f"Язык '{lang_code}' не найден в .env файле")
    else:
        # Удаляем язык из .env
        remove_language_from_env(env_path, lang_code)
    
    # Удаляем язык из всех компонентов приложения
    remove_language_from_models(lang_code)
    remove_language_from_schemas(lang_code)
    remove_language_from_api_mixin(lang_code)
    remove_language_from_lang_schemas(lang_code)
    remove_language_from_translation_utils(lang_code)
    remove_language_from_frontend_types(lang_code)
    remove_language_from_frontend_forms(lang_code)
    
    print(f"Язык '{lang_code}' успешно удален из приложения!")


if __name__ == "__main__":
    from typing import List  # Импортируем здесь, чтобы избежать конфликта с локальной функцией
    main()
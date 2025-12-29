#!/usr/bin/env python3
"""
Скрипт для добавления нового языкового кода в приложение.
Добавляет соответствующие поля в модели, схемы, фронтенд и другие компоненты.
"""
import os
import re
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple


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


def add_language_to_env(env_path: str, lang_code: str) -> bool:
    """Добавляет код языка в переменную LANGS в .env файле"""
    current_langs = get_current_languages_from_env(env_path)
    
    if lang_code in current_langs:
        print(f"Язык '{lang_code}' уже есть в списке: {', '.join(current_langs)}")
        return False
    
    current_langs.append(lang_code)
    new_langs_str = ','.join(current_langs)
    
    # Обновляем .env файл
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = re.sub(r'^LANGS\s*=.*$', f'LANGS={new_langs_str}', content, flags=re.MULTILINE)
    
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Язык '{lang_code}' добавлен в .env. Новое значение: LANGS={new_langs_str}")
    return True


def get_field_suffix(lang_code: str) -> str:
    """Возвращает суффикс для полей на основе языкового кода"""
    if lang_code == 'en':
        return ''  # en по умолчанию без суффикса
    return f'_{lang_code}'


def add_language_to_models(lang_code: str):
    """Добавляет языковые поля в модели SQLAlchemy"""
    model_file = Path("/workspace/app/core/models/base_model.py")
    
    if not model_file.exists():
        print(f"Файл модели не найден: {model_file}")
        return
    
    with open(model_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    suffix = get_field_suffix(lang_code)
    
    # Добавляем комментарии-метки для облегчения поиска
    # Модель BaseDescription
    if suffix:  # Для en не добавляем суффикс
        # Ищем секцию BaseDescription
        description_section_start = content.find("class BaseDescription:")
        if description_section_start != -1:
            # Находим конец секции (следующий класс или конец файла)
            next_class_pos = content.find("\nclass ", description_section_start + 1)
            if next_class_pos == -1:
                next_class_pos = len(content)
            
            section_content = content[description_section_start:next_class_pos]
            
            # Проверяем, есть ли уже поле с таким суффиксом
            if f"description{suffix}:" not in section_content:
                # Находим конец полей в этой секции
                end_of_fields = section_content.rfind("\n    #")
                if end_of_fields == -1:
                    end_of_fields = section_content.rfind("\n\n") or section_content.rfind("\nclass")
                    if end_of_fields == -1:
                        end_of_fields = len(section_content)
                
                # Добавляем новое поле с метками
                new_field = f"    # START_LANG_FIELD_{lang_code.upper()}\n    description{suffix}: Mapped[descr]\n    # END_LANG_FIELD_{lang_code.upper()}\n"
                
                if end_of_fields == len(section_content):
                    updated_section = section_content + new_field
                else:
                    updated_section = section_content[:end_of_fields] + new_field + section_content[end_of_fields:]
                
                # Заменяем секцию в общем контенте
                content = content[:description_section_start] + updated_section + content[next_class_pos:]
    
    # Модель BaseLang
    base_lang_start = content.find("class BaseLang")
    if base_lang_start != -1:
        next_class_pos = content.find("\nclass ", base_lang_start + 1)
        if next_class_pos == -1:
            next_class_pos = len(content)
        
        section_content = content[base_lang_start:next_class_pos]
        
        if f"name{suffix}:" not in section_content and suffix:  # Для en не добавляем суффикс
            # Находим конец полей
            end_of_fields = section_content.rfind("\n    #")
            if end_of_fields == -1:
                end_of_fields = section_content.rfind("\n\n") or section_content.rfind("\nclass")
                if end_of_fields == -1:
                    end_of_fields = len(section_content)
            
            new_field = f"    # START_LANG_FIELD_{lang_code.upper()}\n    name{suffix}: Mapped[str_null_true]\n    # END_LANG_FIELD_{lang_code.upper()}\n"
            
            if end_of_fields == len(section_content):
                updated_section = section_content + new_field
            else:
                updated_section = section_content[:end_of_fields] + new_field + section_content[end_of_fields:]
            
            content = content[:base_lang_start] + updated_section + content[next_class_pos:]
    
    # Обновляем метод __str__ в BaseFullFree
    base_full_free_start = content.find("class BaseFullFree")
    if base_full_free_start != -1:
        # Находим метод __str__
        str_method_start = content.find("def __str__(self)", base_full_free_start)
        if str_method_start != -1:
            # Находим тело метода
            body_start = content.find("return", str_method_start)
            if body_start != -1:
                # Обновляем возвращаемое выражение, добавляя новый язык
                # Находим текущее выражение
                line_end = content.find("\n", body_start)
                if line_end != -1:
                    current_return = content[body_start:line_end].strip()
                    
                    # Обновляем выражение, добавляя новый язык в конец
                    if f"self.name{suffix}" not in current_return:
                        # Заменяем последнюю часть выражения на новую с добавлением языка
                        if lang_code == 'en':
                            # en идет без суффикса
                            new_return = current_return.replace(" or \"\"", f" or self.name or \"\"")
                        else:
                            new_return = current_return.replace(" or \"\"", f" or self.name{suffix} or \"\"")
                        
                        content = content[:body_start] + new_return + content[line_end:]
    
    with open(model_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Языковые поля для '{lang_code}' добавлены в модели SQLAlchemy")


def add_language_to_schemas(lang_code: str):
    """Добавляет языковые поля в Pydantic схемы"""
    schema_file = Path("/workspace/app/core/schemas/base.py")
    
    if not schema_file.exists():
        print(f"Файл схемы не найден: {schema_file}")
        return
    
    with open(schema_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    suffix = get_field_suffix(lang_code)
    
    # Обновляем DescriptionSchema
    if suffix:  # Для en не добавляем суффикс
        desc_schema_start = content.find("class DescriptionSchema")
        if desc_schema_start != -1:
            # Находим конец секции до следующего класса
            next_class_pos = content.find("\n\nclass ", desc_schema_start + 1)
            if next_class_pos == -1:
                next_class_pos = content.find("\n\nclass", desc_schema_start + 1)
            if next_class_pos == -1:
                next_class_pos = len(content)
            
            section_content = content[desc_schema_start:next_class_pos]
            
            # Проверяем, есть ли уже поле с таким суффиксом
            if f"description{suffix}:" not in section_content:
                # Добавляем новое поле перед закрывающей скобкой
                new_field = f"    # START_LANG_FIELD_{lang_code.upper()}\n    description{suffix}: Optional[str] = None\n    # END_LANG_FIELD_{lang_code.upper()}\n"
                
                # Находим место перед последней пустой строкой или перед следующим классом
                end_pos = section_content.rfind("\n    #")
                if end_pos == -1:
                    end_pos = section_content.rfind("\n\n") or section_content.rfind("\nclass")
                    if end_pos == -1:
                        end_pos = len(section_content)
                
                updated_section = section_content[:end_pos] + new_field + section_content[end_pos:]
                content = content[:desc_schema_start] + updated_section + content[next_class_pos:]
    
    # Обновляем NameSchema
    name_schema_start = content.find("class NameSchema")
    if name_schema_start != -1:
        next_class_pos = content.find("\n\nclass ", name_schema_start + 1)
        if next_class_pos == -1:
            next_class_pos = content.find("\n\nclass", name_schema_start + 1)
        if next_class_pos == -1:
            next_class_pos = len(content)
        
        section_content = content[name_schema_start:next_class_pos]
        
        if f"name{suffix}:" not in section_content and suffix:  # Для en не добавляем суффикс
            new_field = f"    # START_LANG_FIELD_{lang_code.upper()}\n    name{suffix}: Optional[str] = None\n    # END_LANG_FIELD_{lang_code.upper()}\n"
            
            end_pos = section_content.rfind("\n    #")
            if end_pos == -1:
                end_pos = section_content.rfind("\n\n") or section_content.rfind("\nclass")
                if end_pos == -1:
                    end_pos = len(section_content)
            
            updated_section = section_content[:end_pos] + new_field + section_content[end_pos:]
            content = content[:name_schema_start] + updated_section + content[next_class_pos:]
    
    # Обновляем DescriptionExcludeSchema
    desc_excl_schema_start = content.find("class DescriptionExcludeSchema")
    if desc_excl_schema_start != -1:
        next_class_pos = content.find("\n\nclass ", desc_excl_schema_start + 1)
        if next_class_pos == -1:
            next_class_pos = content.find("\n\nclass", desc_excl_schema_start + 1)
        if next_class_pos == -1:
            next_class_pos = len(content)
        
        section_content = content[desc_excl_schema_start:next_class_pos]
        
        if f"description{suffix}:" not in section_content and suffix:
            new_field = f"    # START_LANG_FIELD_{lang_code.upper()}\n    description{suffix}: Optional[str] = Field(exclude=True)\n    # END_LANG_FIELD_{lang_code.upper()}\n"
            
            end_pos = section_content.rfind("\n    #")
            if end_pos == -1:
                end_pos = section_content.rfind("\n\n") or section_content.rfind("\nclass")
                if end_pos == -1:
                    end_pos = len(section_content)
            
            updated_section = section_content[:end_pos] + new_field + section_content[end_pos:]
            content = content[:desc_excl_schema_start] + updated_section + content[next_class_pos:]
    
    # Обновляем NameExcludeSchema
    name_excl_schema_start = content.find("class NameExcludeSchema")
    if name_excl_schema_start != -1:
        next_class_pos = content.find("\n\nclass ", name_excl_schema_start + 1)
        if next_class_pos == -1:
            next_class_pos = content.find("\n\nclass", name_excl_schema_start + 1)
        if next_class_pos == -1:
            next_class_pos = len(content)
        
        section_content = content[name_excl_schema_start:next_class_pos]
        
        if f"name{suffix}:" not in section_content and suffix:
            new_field = f"    # START_LANG_FIELD_{lang_code.upper()}\n    name{suffix}: Optional[str] = Field(exclude=True)\n    # END_LANG_FIELD_{lang_code.upper()}\n"
            
            end_pos = section_content.rfind("\n    #")
            if end_pos == -1:
                end_pos = section_content.rfind("\n\n") or section_content.rfind("\nclass")
                if end_pos == -1:
                    end_pos = len(section_content)
            
            updated_section = section_content[:end_pos] + new_field + section_content[end_pos:]
            content = content[:name_excl_schema_start] + updated_section + content[next_class_pos:]
    
    with open(schema_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Языковые поля для '{lang_code}' добавлены в Pydantic схемы")


def add_language_to_api_mixin(lang_code: str):
    """Добавляет языковые поля в API mixin"""
    mixin_file = Path("/workspace/app/core/schemas/api_mixin.py")
    
    if not mixin_file.exists():
        print(f"Файл api_mixin не найден: {mixin_file}")
        return
    
    with open(mixin_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    suffix = get_field_suffix(lang_code)
    
    if suffix:  # Для en не добавляем суффикс
        # Проверяем, есть ли уже такое поле
        if f"def name{suffix}(self)" not in content:
            # Находим конец класса
            class_end = content.rfind("\n\n", content.find("class LangMixin"))
            if class_end == -1:
                class_end = len(content)
            
            # Добавляем новое свойство перед концом класса
            new_property = f"""
    @computed_field
    @property
    def name{suffix}(self) -> str:
        return self.__get_lang__('{suffix}')
"""
            
            content = content[:class_end] + new_property + content[class_end:]
    
    with open(mixin_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Языковое поле для '{lang_code}' добавлено в API mixin")


def add_language_to_lang_schemas(lang_code: str, display_name: str, description_name: str):
    """Добавляет языковые схемы для нового языка"""
    lang_schema_file = Path("/workspace/app/core/schemas/lang_schemas.py")
    
    if not lang_schema_file.exists():
        print(f"Файл lang_schemas не найден: {lang_schema_file}")
        return
    
    with open(lang_schema_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем, существует ли уже схема для этого языка
    if f"ListView{lang_code.upper()}" in content:
        print(f"Языковые схемы для '{lang_code}' уже существуют")
        return
    
    # Создаем новые схемы для языка
    new_schemas = f"""
# START_LANG_SCHEMA_{lang_code.upper()}
class ListView{lang_code.upper()}(ListView):
    @computed_field(description='{display_name}',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        \"\"\"Возвращает первое непустое значение из name, name_ru, name_fr и других языков\"\"\"
        # Формируем список полей в приоритетном порядке
        fields = ['name_{lang_code}']  # Добавляем поле нового языка
        # Добавляем другие языки в порядке приоритета
        all_fields = ['name']
        # Сначала en, потом ru, fr, потом новый язык
        for existing_lang in ['en', 'ru', 'fr']:
            if existing_lang != lang_code:
                all_fields.append(f'name_{existing_lang}')
        all_fields.append(f'name_{lang_code}')
        
        for field in all_fields:
            if field == 'name':
                value = getattr(self, 'name', None)
            else:
                value = getattr(self, field, None)
            if value:
                return value
        return ""


class DetailView{lang_code.upper()}(DetailView):
    @computed_field(description='{display_name}',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        \"\"\"Возвращает первое непустое значение из name, name_ru, name_fr и других языков\"\"\"
        # Формируем список полей в приоритетном порядке
        fields = [f'name_{lang_code}']  # Добавляем поле нового языка
        # Добавляем другие языки в порядке приоритета
        all_fields = ['name']
        # Сначала en, потом ru, fr, потом новый язык
        for existing_lang in ['en', 'ru', 'fr']:
            if existing_lang != lang_code:
                all_fields.append(f'name_{existing_lang}')
        all_fields.append(f'name_{lang_code}')
        
        for field in all_fields:
            if field == 'name':
                value = getattr(self, 'name', None)
            else:
                value = getattr(self, field, None)
            if value:
                return value
        return ""

    @computed_field(description='{description_name}',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_description(self) -> str:
        # Формируем список полей в приоритетном порядке
        fields = [f'description_{lang_code}']  # Добавляем поле нового языка
        # Добавляем другие языки в порядке приоритета
        all_fields = ['description']
        # Сначала en, потом ru, fr, потом новый язык
        for existing_lang in ['en', 'ru', 'fr']:
            if existing_lang != lang_code:
                all_fields.append(f'description_{existing_lang}')
        all_fields.append(f'description_{lang_code}')
        
        for field in all_fields:
            if field == 'description':
                value = getattr(self, 'description', None)
            else:
                value = getattr(self, field, None)
            if value:
                return value
        return ""
# END_LANG_SCHEMA_{lang_code.upper()}
"""
    
    # Добавляем новые схемы в конец файла
    content += new_schemas
    
    with open(lang_schema_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Языковые схемы для '{lang_code}' добавлены")


def add_language_to_translation_utils(lang_code: str):
    """Добавляет поддержку нового языка в утилиты перевода"""
    translation_file = Path("/workspace/app/core/utils/translation_utils.py")
    
    if not translation_file.exists():
        print(f"Файл translation_utils не найден: {translation_file}")
        return
    
    with open(translation_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Обновляем функцию get_localized_fields
    # Находим список полей
    if f"'name_{lang_code}'" not in content:
        content = content.replace(
            "return [\n        'name', 'name_fr', 'name_ru',",
            f"return [\n        'name', 'name_fr', 'name_ru', 'name_{lang_code}',"
        )
        content = content.replace(
            "'description', 'description_fr', 'description_ru',",
            f"'description', 'description_fr', 'description_ru', 'description_{lang_code}',"
        )
        # Добавляем также title и subtitle если они есть
        content = content.replace(
            "'title', 'title_fr', 'title_ru',",
            f"'title', 'title_fr', 'title_ru', 'title_{lang_code}',"
        )
        content = content.replace(
            "'subtitle', 'subtitle_fr', 'subtitle_ru',",
            f"'subtitle', 'subtitle_fr', 'subtitle_ru', 'subtitle_{lang_code}',"
        )
    
    # Обновляем функцию get_field_language
    if f"elif field_name.endswith('_{lang_code}'):" not in content:
        # Находим место перед закрывающим return None
        content = content.replace(
            "    elif field_name.endswith('_fr'):\n        return 'fr'",
            f"    elif field_name.endswith('_fr'):\n        return 'fr'\n    elif field_name.endswith('_{lang_code}'):\n        return '{lang_code}'"
        )
    
    # Обновляем функцию get_base_field_name
    if f"_{lang_code}'" not in content:
        content = content.replace(
            "if field_name.endswith(('_ru', '_fr')):",
            f"if field_name.endswith(('_ru', '_fr', '_{lang_code}')):"
        )
    
    with open(translation_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Поддержка языка '{lang_code}' добавлена в утилиты перевода")


def add_language_to_frontend_types(lang_code: str):
    """Добавляет языковые поля в TypeScript типы"""
    types_file = Path("/workspace/preact_front/src/types/base.ts")
    
    if not types_file.exists():
        print(f"Файл TypeScript типов не найден: {types_file}")
        return
    
    with open(types_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Добавляем поля в интерфейс LangFields
    lang_fields_start = content.find("export interface LangFields")
    if lang_fields_start != -1:
        next_bracket = content.find("}", lang_fields_start)
        if next_bracket != -1:
            section_content = content[lang_fields_start:next_bracket]
            
            if f"name_{lang_code}?: string;" not in section_content:
                new_field = f"  // START_LANG_FIELD_{lang_code.upper()}\n  name_{lang_code}?: string;\n  description_{lang_code}?: string;\n  // END_LANG_FIELD_{lang_code.upper()}\n"
                content = content[:next_bracket] + new_field + content[next_bracket:]
    
    with open(types_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Языковые поля для '{lang_code}' добавлены в TypeScript типы")


def add_language_to_frontend_forms(lang_code: str):
    """Добавляет языковые поля в формы фронтенда"""
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
        
        # Добавляем поля в начальное состояние формы
        # Ищем пустые строки для новых полей
        if f"title_{lang_code}" not in content:
            # Добавляем поля в начальное состояние
            content = content.replace(
                "title_ru: '',",
                f"title_ru: '',\n    title_{lang_code}: '',"
            )
            content = content.replace(
                "title_fr: '',",
                f"title_fr: '',\n    title_{lang_code}: '',"
            )
            
            content = content.replace(
                "subtitle_ru: '',",
                f"subtitle_ru: '',\n    subtitle_{lang_code}: '',"
            )
            content = content.replace(
                "subtitle_fr: '',",
                f"subtitle_fr: '',\n    subtitle_{lang_code}: '',"
            )
            
            content = content.replace(
                "description_ru: '',",
                f"description_ru: '',\n    description_{lang_code}: '',"
            )
            content = content.replace(
                "description_fr: '',",
                f"description_fr: '',\n    description_{lang_code}: '',"
            )
        
        # Добавляем поля в input элементы
        if f'name="title_{lang_code}"' not in content:
            # Добавляем input для title
            content = content.replace(
                'name="title_fr"',
                f'name="title_{lang_code}"\n                    value={{{{"{{"}}formData.title_{lang_code}{{"}}"}}}\n                    onChange={handleChange}\n                    className="form-input"\n                  />\n                  <input\n                    type="text"\n                    name="title_fr"'
            )
            
            # Добавляем input для subtitle
            content = content.replace(
                'name="subtitle_fr"',
                f'name="subtitle_{lang_code}"\n                    value={{{{"{{"}}formData.subtitle_{lang_code}{{"}}"}}}\n                    onChange={handleChange}\n                    className="form-input"\n                  />\n                  <input\n                    type="text"\n                    name="subtitle_fr"'
            )
            
            # Добавляем input для description
            content = content.replace(
                'name="description_fr"',
                f'name="description_{lang_code}"\n                    value={{{{"{{"}}formData.description_{lang_code}{{"}}"}}}\n                    onChange={handleChange}\n                    className="form-input"\n                  />\n                  <input\n                    type="text"\n                    name="description_fr"'
            )
        
        with open(form_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f"Языковые поля для '{lang_code}' добавлены в формы фронтенда")


def main():
    parser = argparse.ArgumentParser(description='Добавить новый языковой код в приложение')
    parser.add_argument('lang_code', help='Двухбуквенный код языка (например, de, es, it)')
    parser.add_argument('--display-name', help='Отображаемое имя для языка (например, German, Spanish)', default='Name')
    parser.add_argument('--description-name', help='Отображаемое имя для описания (например, Beschreibung)', default='Description')
    
    args = parser.parse_args()
    
    lang_code = args.lang_code.lower()
    
    # Проверяем код языка
    if not validate_language_code(lang_code):
        print(f"Ошибка: '{lang_code}' не является допустимым двухбуквенным кодом языка")
        sys.exit(1)
    
    # Проверяем, есть ли такой язык уже в .env
    env_path = "/workspace/.env"
    current_langs = get_current_languages_from_env(env_path)
    
    if lang_code in current_langs:
        print(f"Язык '{lang_code}' уже есть в .env файле")
    else:
        # Добавляем язык в .env
        add_language_to_env(env_path, lang_code)
    
    # Добавляем язык во все компоненты приложения
    add_language_to_models(lang_code)
    add_language_to_schemas(lang_code)
    add_language_to_api_mixin(lang_code)
    add_language_to_lang_schemas(lang_code, args.display_name, args.description_name)
    add_language_to_translation_utils(lang_code)
    add_language_to_frontend_types(lang_code)
    add_language_to_frontend_forms(lang_code)
    
    print(f"Язык '{lang_code}' успешно добавлен в приложение!")


if __name__ == "__main__":
    main()
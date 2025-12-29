#!/usr/bin/env python3
"""
Главный скрипт для управления языками в приложении.
Объединяет функциональность добавления и удаления языковых полей.
"""
import os
import sys
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Управление языками в приложении')
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')
    
    # Подкоманда для добавления языка
    add_parser = subparsers.add_parser('add', help='Добавить новый язык')
    add_parser.add_argument('lang_code', help='Двухбуквенный код языка (например, de, es, it)')
    add_parser.add_argument('--display-name', help='Отображаемое имя для языка (например, German, Spanish)', default='Name')
    add_parser.add_argument('--description-name', help='Отображаемое имя для описания (например, Beschreibung)', default='Description')
    
    # Подкоманда для удаления языка
    remove_parser = subparsers.add_parser('remove', help='Удалить язык')
    remove_parser.add_argument('lang_code', help='Двухбуквенный код языка (например, de, es, it)')
    
    args = parser.parse_args()
    
    if args.command == 'add':
        # Импортируем и вызываем функцию добавления языка
        import subprocess
        result = subprocess.run([
            sys.executable, './add_language.py', 
            args.lang_code, 
            '--display-name', args.display_name, 
            '--description-name', args.description_name
        ], cwd='/workspace/scripts/language')
        sys.exit(result.returncode)
    elif args.command == 'remove':
        # Импортируем и вызываем функцию удаления языка
        import subprocess
        result = subprocess.run([
            sys.executable, './remove_language.py', 
            args.lang_code
        ], cwd='/workspace/scripts/language')
        sys.exit(result.returncode)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
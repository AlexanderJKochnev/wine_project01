# app/core/utils/io_utils.py
from pathlib import Path
from app.core.utils.common_utils import get_path_to_root, enum_to_camel
from app.core.config.project_config import settings


def read_file_lines_stripped(filename: Path):
    """ читает файл построчно и возвращает список
        filename имя файла
        dirname директория в которой находится файл (если файл глде-то в боковой ветке)
        для получения filename используй from app.core.utils.common_utils import get_path_to_root
    """
    with open(filename, 'r', encoding='utf-8') as file:
        return [line.rstrip('\n').rstrip(';').strip() for line in file]


def read_enum_to_camel(filename: str = 'country.json') -> dict:
    """
        берет файл в директории загрузки считывает и возвращает словарь
        :param filename:  имя файла
        :type filename:   str
        :return:          {'исходная_строка': 'Исходная Строка'}
        :rtype:           dict
    """
    try:
        upload_dir = settings.UPLOAD_DIR
        file = 'country.json'
        dirname = get_path_to_root(f'{upload_dir}')
        filepath = dirname / file
        result = read_file_lines_stripped(filepath)
        result = {a: enum_to_camel(a) for a in result}
    except Exception as e:
        print(f'read_enum_to_camel.error: {e}')
        result = None
    finally:
        return result

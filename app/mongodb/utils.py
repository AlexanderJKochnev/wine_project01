# app/mongodb/utils.py
import string
import mimetypes
import random
from app.mongodb.config import settings
from fastapi import UploadFile, HTTPException
import os
import magic
from pathlib import Path
from typing import List, Tuple
import io
from PIL import Image


def make_transparent_white_bg(content: bytes) -> bytes:
    """ удаление белого (почти белого) фона"""
    # Открываем изображение
    img = Image.open(io.BytesIO(content))

    # Конвертируем в RGBA (добавляем альфа-канал для прозрачности)
    img = img.convert("RGBA")

    # Получаем данные пикселей
    datas = img.getdata()

    # Создаем новый список пикселей
    new_data = []

    # Заменяем белый цвет (или близкий к белому) на прозрачный
    for item in datas:
        # Если пиксель белый (или близок к белому), делаем прозрачным
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            new_data.append((255, 255, 255, 0))  # прозрачный
        else:
            new_data.append(item)

    # Обновляем данные изображения
    img.putdata(new_data)

    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    return img_bytes.getvalue()


def remove_background(content: bytes, bg_color=(255, 255, 255), tolerance=20) -> bytes:
    """
    Удаляет фон указанного цвета с заданной допуском
    """
    img = Image.open(io.BytesIO(content))
    img = img.convert("RGBA")

    datas = img.getdata()
    new_data = []

    for item in datas:
        # Проверяем, насколько цвет близок к фону
        if (abs(item[0] - bg_color[0]) <= tolerance and abs(item[1] - bg_color[1]) <= tolerance and abs(
                item[2] - bg_color[2]) <= tolerance):
            # Делаем прозрачным
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)

    img.putdata(new_data)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    return img_bytes.getvalue()


def remove_background_with_mask(content: bytes) -> bytes:
    """
    удаление фона по маске
    """
    img = Image.open(io.BytesIO(content))

    # Создаем маску на основе альфа-канала или яркости
    if img.mode == 'RGBA':
        # Если уже есть альфа-канал, используем его как маску
        alpha = img.split()[-1]
    else:
        # Иначе создаем маску на основе яркости
        img_gray = img.convert('L')
        alpha = img_gray.point(lambda x: 0 if x > 240 else 255)

    # Создаем изображение с прозрачностью
    img_rgba = img.convert('RGBA')
    img_rgba.putalpha(alpha)

    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    return img_bytes.getvalue()


def file_name(origin: str, length: int = 10, ext: str = None) -> str:
    """
    меняет имя файла на произвольное
    :param origin: исходное имя
    :param length: заданная длина
    :return: имя файла с расширением
    """
    if not ext:
        ext = f".{origin.rsplit('.', 1)}" if '.' in origin else ''
    name = ''.join(random.choice(string.ascii_letters) for _ in range(length))
    return f'{name}{ext}'


def image_aligning(content):
    """ подгон изображения под требуемый разимер"""
    width = settings.IMAGE_WIDTH
    height = settings.IMAGE_HEIGH
    # quality = settings.IMAGE_QUALITY
    try:
        # Открываем изображение
        image = Image.open(io.BytesIO(content))
        original_width, original_height = image.size
        original_ratio = original_width / original_height
        ratio = width / height
        if original_ratio > ratio:
            # height priority
            new_height = height
            new_width = int(original_width * (height / original_height))
        else:
            # width_priority
            new_width = width
            new_height = int(original_height * (width / original_width))
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        img_byte_arr = io.BytesIO()
        format = image.format if image.format else 'JPEG'
        resized_image.save(img_byte_arr, format=format, optimize=True)
        # Получаем обработанное содержимое
        new_content = img_byte_arr.getvalue()
        return new_content
    except Exception as e:
        return content
        raise HTTPException(status_code=400, detail=f"Ошибка обработки изображения: {str(e)}")


class ContentTypeDetector:
    """Класс для определения типа контента"""

    @staticmethod
    async def detect(file: UploadFile) -> str:
        """Определяет content_type файла"""

        # 1. Пробуем получить из заголовков HTTP
        if file.content_type:
            return file.content_type

        # 2. Пробуем определить по расширению
        extension_type = ContentTypeDetector._by_extension(file.filename)
        if extension_type != 'application/octet-stream':
            return extension_type

        # 3. Определяем по содержимому
        content = await file.read()
        content_type = ContentTypeDetector._by_content(content)

        # Возвращаем указатель файла в начало
        await file.seek(0)

        return content_type

    @staticmethod
    def _by_extension(filename: str) -> str:
        """Определяет по расширению файла"""
        extension = os.path.splitext(filename)[1].lower()
        types = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.jpe': 'image/jpeg', '.png': 'image/png',
                 '.gif': 'image/gif', '.bmp': 'image/bmp', '.webp': 'image/webp', '.svg': 'image/svg+xml',
                 '.tiff': 'image/tiff', '.tif': 'image/tiff', '.heic': 'image/heic', '.heif': 'image/heif', }
        return types.get(extension, 'application/octet-stream')

    @staticmethod
    def _by_content(content: bytes) -> str:
        """Определяет по содержимому файла"""
        try:
            # Используем python-magic если установлен
            return magic.from_buffer(content, mime=True)
        except ImportError:
            # Fallback на ручное определение
            return ContentTypeDetector._by_content_manual(content)

    @staticmethod
    def _by_content_manual(content: bytes) -> str:
        """Ручное определение по сигнатурам"""
        if len(content) < 8:
            return 'application/octet-stream'

        signatures = {b'\xff\xd8\xff': 'image/jpeg',  # JPEG
                      b'\x89PNG\r\n\x1a\n': 'image/png',  # PNG
                      b'GIF87a': 'image/gif',  # GIF
                      b'GIF89a': 'image/gif',  # GIF
                      b'RIFF....WEBPVP': 'image/webp',  # WebP
                      b'BM': 'image/bmp',  # BMP
                      b'II*\x00': 'image/tiff',  # TIFF little-endian
                      b'MM\x00*': 'image/tiff',  # TIFF big-endian
                      }

        for signature, mime_type in signatures.items():
            if content.startswith(signature):
                return mime_type

        return 'application/octet-stream'


class TestFileUtils:
    """Утилиты для работы с тестовыми файлами"""

    @staticmethod
    def get_test_images(directory: Path) -> List[Path]:
        """Возвращает список путей к тестовым изображениям"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff'}
        return [f for f in directory.iterdir() if f.is_file() and f.suffix.lower() in image_extensions]

    @staticmethod
    def read_image_file(image_path: Path) -> Tuple[bytes, str, int]:
        """Читает файл изображения и возвращает (content, content_type, size)"""
        with open(image_path, 'rb') as f:
            content = f.read()

        content_type = TestFileUtils.get_content_type(image_path)
        size = len(content)

        return content, content_type, size

    @staticmethod
    def get_content_type(image_path: Path) -> str:
        """Определяет MIME-type по расширению файла"""
        extension = image_path.suffix.lower()
        types = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.gif': 'image/gif',
                 '.webp': 'image/webp', '.bmp': 'image/bmp', '.tiff': 'image/tiff', '.tif': 'image/tiff',
                 '.svg': 'image/svg+xml'}
        return types.get(extension, 'application/octet-stream')

    @staticmethod
    def create_test_image(format: str = 'JPEG', size: Tuple[int, int] = (100, 100)) -> Tuple[bytes, str]:
        """Создает тестовое изображение в памяти"""
        image = Image.new('RGB', size, color='blue')
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=format)

        mime_types = {'JPEG': 'image/jpeg', 'PNG': 'image/png', 'GIF': 'image/gif'}
        return img_byte_arr.getvalue(), mime_types.get(format, 'image/jpeg')


def read_image_generator(filepath_list: List[str]):
    """ читает и преолбразует файлы изображений из списка в вид пригодный для загрузки """
    for n, item in enumerate(filepath_list):
        with open(item, "rb") as f:
            try:
                test_image_data = f.read()
                content_type, _ = mimetypes.guess_type(str(item))
                content_type = content_type or "application/octet-stream"
                upload_file = UploadFile(file=io.BytesIO(test_image_data),
                                         filename=item.name)
                yield upload_file
            except Exception as e:
                raise Exception(f'read_image_generator: {e}')
            """
            content = upload_file.read()
            # удаляем фон 3 способа доработать
            try:
                # content = make_transparent_white_bg(content)
                content = remove_background(content)
                # content = remove_background_with_mask(content)
                content_type = 'image/png'
                filename = f'{item.stem}.png'
            except Exception as e:
                print(f'Удаление фона не получилось для {item.name}. {e}. Оставляем без изменения')
            # подгоняем размер
            try:
                if len(content) > 8 * 1024 * 1024:
                    content = image_aligning(content)
            except Exception as e:
                print(f'Изменение размера не получилось для {item.name}. {e}. Оставляем без изменения')
            description = f'импортированный файл {datetime.now(timezone.utc)}'
        yield filename, content, content_type, description
        """

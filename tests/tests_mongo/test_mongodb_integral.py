import pytest
from bson import ObjectId
from fastapi import status

from app.core.utils.common_utils import jprint
from app.mongodb.router import (fileprefix, prefix, directprefix,
                                subprefix)  # Импортируем префиксы для корректного URL
pytestmark = pytest.mark.asyncio

# Предполагается, что следующие фикстуры определены с scope="function" в conftest.py
# @pytest.fixture(scope="function")
# def mock_mongodb_database():
#     # ...
#
# @pytest.fixture(scope="function")
# def client(mock_mongodb_database):
#     # ...
#
# @pytest.fixture(scope="function")
# def mock_user():
#     # ...


async def test_mongodb_image_crud_and_lists(authenticated_client_with_db,
                                            test_db_session, sample_image_paths,
                                            test_images_dir,
                                            todayutc,
                                            futureutc,
                                            pastutc
                                            ):
    """
    Тестирует основные CRUD операции и списки для изображений в MongoDB в одной функции.
    Это необходимо из-за scope="function" у фикстур подключения к базе данных.
    """
    # from app.mongodb.models import ImageCreateResponse
    client = authenticated_client_with_db
    # fake_png_content = (b'\x89PNG\r\n\x1a\n\x00\x00\x00\r')
    # Используем правильный формат для httpx: (field_name, (filename, file_content, content_type))
    # upload_file = ("file", ("test_upload.png", fake_png_content, "image/png"))

    # Словарь для хранения результатов и ошибок
    test_results = {}
    errors = []
    created_file_ids = []
    created_filenames = []

    # получаем несколько изображений из тестовой директории
    for n, image in enumerate(sample_image_paths):
        # --- 1. Тест: Успешная загрузка изображения ---
        with open(image, 'rb') as f:
            image_content = f.read()
        file_name = image.name
        data = {"description": "Test image for integration test"}
        files = {"file": (file_name, image_content)}
        response = await client.post(f'{prefix}/{subprefix}', files=files, data=data)
        # Проверяем успешность запроса
        status_ok = response.status_code == status.HTTP_200_OK
        test_results[f'1. Upload status code. Tier {n}'] = status_ok
        if not status_ok:
            assert False, 'ошибка загрузки файла - остальные тесты выполнимт невозможно'
        result = response.json()
        # проверка наличия id
        status_ok = result.get('id') is not None
        test_results[f'2. Uploade file has id. Tier {n}'] = status_ok
        if status_ok:
            created_file_id = result["id"]
            created_file_ids.append(created_file_id)
        # проверка соотвествия имении файла оригиналу
        status_ok = file_name == result.get('filename')
        created_filename = result.get('filename')
        created_filenames.append(created_filename)
        # test_results[f'3. Filename is the same. Tier {n}'] = status_ok
        # Проверяем создание thumbnail
        status_ok = result.get('has_thumbnail')
        test_results[f'4. Thumbnail has been generated. Tier {n}'] = status_ok

    # Если загрузка прошла успешно, продолжаем остальные тесты CRUD
    if not all((created_file_id, created_filename)):
        jprint(test_results)
        assert False, 'ошибка при загрузке. см результат выше'
    # получение cписка с пагинацией (разные варианты
    params = [({"page": 1, "per_page": 10}, 200, n),
              ({"page": 1, "per_page": 10, "after_date": pastutc}, 200, n),
              ({"page": 1, "per_page": 10, "after_date": todayutc}, 200, 0),
              ({"page": 1, "per_page": 10, "after_date": futureutc}, 400, 0), ]
    for n, (param, sts, nmb) in enumerate(params):
        try:
            response = await client.get(f"{prefix}/{subprefix}", params=param)
            status_ok = response.status_code == sts
            test_results[f'Get paginated list. Tier {n}'] = status_ok
            param = {'after_date': param.get('after_date')} if param.get('after_date') else None
            if param:
                response = await client.get(f"{prefix}/{subprefix}list", params=param)
            else:
                response = await client.get(f"{prefix}/{subprefix}list")
            status_ok = response.status_code == sts
            test_results[f'Get non-paginated list. Tier {n}'] = status_ok
        except Exception as e:
            assert False, f'{param=},  {e}'

    # --- 4. Тест: Получение thumbnail по ID ---
    # Этот вызов может создать thumbnail в БД, если его нет, через логику сервиса.
    response = await client.get(f"/{prefix}/{subprefix}/{created_file_ids[0]}")
    status_ok = response.status_code == 200
    test_results['ThumbnailByID status code'] = status_ok
    header_ok = response.headers.get("X-Image-Type") == "thumbnail"
    test_results['ThumbnailByID header type'] = header_ok

    # --- 5. Тест: Получение полного изображения по ID ---
    response = await client.get(f"/{prefix}/{subprefix}/full/{created_file_id}")
    status_ok = response.status_code == 200
    test_results['FullByID status code'] = status_ok
    header_ok = response.headers.get("X-Image-Type") == "full"
    test_results['FullByID header type'] = header_ok

    # --- 6. Тест: Получение thumbnail по имени файла ---
    response = await client.get(f"/{prefix}/{fileprefix}/{created_filenames[0]}")
    status_ok = response.status_code == 200
    test_results['ThumbnailByFilename status code'] = status_ok
    header_ok = response.headers.get("X-Image-Type") == "thumbnail"
    test_results['ThumbnailByFilename header type'] = header_ok

    # --- 7. Тест: Получение полного изображения по имени файла ---
    response = await client.get(f"/{prefix}/{fileprefix}/full/{created_filenames[0]}")
    status_ok = response.status_code == 200
    test_results['FullByFilename status code'] = status_ok
    header_ok = response.headers.get("X-Image-Type") == "full"
    test_results['FullByFilename header type'] = header_ok

    # --- 8. Тест: Успешное удаление изображения ---
    response = await client.delete(f"/{prefix}/{subprefix}/{created_file_ids[0]}")
    status_ok = response.status_code == 200
    test_results['Delete status code'] = status_ok
    success_msg = response.json().get("message") == "Image deleted successfully"
    test_results['Delete success message'] = success_msg

    # --- 9. Тест: Попытка получить удаленный thumbnail по ID (ошибка) ---
    response = await client.get(f"/{prefix}/{subprefix}/{created_file_ids[0]}")
    status_ok = response.status_code == 500  # Ожидаем 500 из-за логики роутера
    test_results['GetDeletedThumb status code'] = status_ok

    # --- 10. Тест: Попытка получить удаленный full по ID (ошибка) ---
    response = await client.get(f"/{prefix}/{subprefix}/full/{created_file_ids[0]}")
    status_ok = response.status_code == 404  # Ожидаем 400 из-за логики роутера
    test_results['GetDeletedFull status code'] = status_ok

    # --- 11. Тест: Попытка удалить несуществующий файл (ошибка) ---
    non_existent_id = str(ObjectId())
    response = await client.delete(f"/{prefix}/{subprefix}/{non_existent_id}")
    status_ok = response.status_code == 404  # Ожидаем 400 из-за логики роутера
    test_results['DeleteNonExistent status code'] = status_ok

    # --- 12. Тест: Загрузка с ошибкой валидации (например, слишком большой файл) ---
    # Теперь мы мокаем *метод* upload_image *внутри* ThumbnailImageService на уровне *реализации*,
    # чтобы он бросил исключение, как если бы произошла ошибка на этапе обработки.
    # Это нужно делать *внутри* контекста моков для загрузки, чтобы не повлиять на предыдущую загрузку.
    # Лучше вынести в отдельный блок, чтобы не перезаписывать моки из загрузки.
    # Однако, если мы мокаем весь сервис, он будет мокированным и для CRUD.
    # Нужно быть аккуратным. Лучше мокать *на время* выполнения конкретного запроса.
    # Используем patch на уровне вызова метода сервиса в роутере.
    # Но чтобы роутер вызвал мок, нужно мокировать до его вызова.
    # В роутере `upload_image` использует `image_service: ThumbnailImageService = Depends()`.
    # DI предоставит реальный объект, если мы не мокаем его зависимость.
    # Если мы хотим мокнуть *метод* реального сервиса, не заменяя весь сервис, можно использовать patch.object.
    # Патчим метод *внутри* реального класса *только на время этого вызова*.
    """from app.mongodb.service import ThumbnailImageService
    with patch.object(ThumbnailImageService, 'upload_image', side_effect=Exception("File too large")):
        response = await client.post(
            f"/{prefix}/{subprefix}",
            files=[upload_file],  # Используем тот же файл
            data={"description": "Test upload description for bad case"}
        )
    status_ok = response.status_code == 400
    test_results['BadUpload status code'] = status_ok
    detail_ok = "File too large" in response.json().get("detail", "")
    test_results['BadUpload detail check'] = detail_ok

    # --- 13. Тест: Получение списка с ошибкой валидации даты ---
    response = await client.get(f"/{prefix}/{subprefix}?after_date=invalid-date-format")
    status_ok = response.status_code == 400
    test_results['BadDateList status code'] = status_ok
    detail_present = "detail" in response.json()
    test_results['BadDateList has detail'] = detail_present
    """

    # --- Финальная проверка ---
    # Собираем все проваленные проверки
    failed_checks = [name for name, passed in test_results.items() if not passed]

    # Выводим результаты в табличном виде в консоль
    print("\n" + "=" * 80)
    print(f"{'Тест':<40} | {'Результат':<15} | {'Описание ошибки':<20}")
    print("-" * 80)
    for name, passed in test_results.items():
        result_str = "ПРОЙДЕН" if passed else "ПРОВАЛЕН"
        error_desc = "OK" if passed else "Проверка не пройдена"
        print(f"{name:<40} | {result_str:<15} | {error_desc:<20}")
    if errors:
        for i, error in enumerate(errors):
            print(f"{'Доп. ошибка #' + str(i + 1):<40} | {'ПРОВАЛЕН':<15} | {error:<20}")
    print("=" * 80)
    print(f"Всего проверок: {len(test_results)}, Провалено: {len(failed_checks)}, Доп. ошибок: {len(errors)}")

    if failed_checks or errors:
        # Если есть ошибки или проваленные проверки, объединяем их и выбрасываем AssertionError
        # all_failures = failed_checks + errors
        error_message = f"Тест не пройден. Проваленные проверки: {failed_checks}. Дополнительные ошибки: {errors}"
        assert False, error_message
    else:
        print("✅ Все тесты CRUD и списков пройдены успешно в одной функции.")
        assert True  # Явно указываем, что тест пройден, если нет ошибок

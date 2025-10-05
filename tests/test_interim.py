# tests/test_interim.py
"""
    тестирование всякоразного
"""
from pathlib import Path
# from fastapi import status
import pytest
from app.core.config.project_config import settings
from app.core.utils.common_utils import jprint  # NOQA: F401
from pydantic import ValidationError
from app.core.utils.io_utils import get_filepath_from_dir_by_name
from app.support.item.schemas import ItemCreateRelations, DrinkCreateRelations  # noqa: F401

pytestmark = pytest.mark.asyncio


def test_get_path_to_root():
    from app.core.utils.common_utils import get_path_to_root, enum_to_camel
    from app.core.utils.io_utils import read_file_lines_stripped
    upload_dir = settings.UPLOAD_DIR
    file = 'country.json'
    dirname = get_path_to_root(f'{upload_dir}')
    assert dirname, f'file of directory "{upload_dir}" is not exist'
    assert isinstance(dirname, Path), 'method "get_path_to_root" return unexpected result'
    filepath = dirname / file
    result = read_file_lines_stripped(filepath)
    assert isinstance(result, list)
    expected_result = {a: enum_to_camel(a) for a in result}
    assert isinstance(expected_result, dict)


def test_enum_to_camel_and_back():
    """
        тестирует методы
        read_enum_to_camel
        enum_to_camel
        camel_to_enum
    """
    from app.core.utils.io_utils import read_enum_to_camel
    from app.core.utils.common_utils import enum_to_camel, camel_to_enum
    file = 'country.json'
    result = read_enum_to_camel(file)
    assert isinstance(result, dict)
    for key, val in result.items():
        assert enum_to_camel(key) == val, f'1: {key=} {val=} {enum_to_camel(key)=}'
        assert camel_to_enum(val) == key, f'2: {key=} {val=} {camel_to_enum(val)=}'


def test_get_filepath_from_dir():
    """
    тестирование метода get_filepath_from_dir
    проверяем как работает без аргументов
    """
    from app.core.utils.io_utils import get_filepath_from_dir
    result = get_filepath_from_dir()
    assert isinstance(result, list), f'получен неожидаемый ответ  {type(result)}'
    for key in result:
        assert isinstance(key, Path), f'ответ не сооветствует ожидаемому. {key}'


def test_get_filepath_from_dir_by_name():
    """
    тестирование метода get_filepath_from_dir_by_name (получение data.json)
    """
    result = get_filepath_from_dir_by_name()
    assert isinstance(result, Path), f'получен неожидаемый ответ  {type(result)}'


def test_jsonconverter():
    """
    тестирует from app.core.utils.io_utils import loadJsonConverter
    тестирует исходные данные (если выбрасывает - см. diff
    """
    from app.core.utils.alchemy_utils import JsonConverter
    filepath = get_filepath_from_dir_by_name()
    JsonConv = JsonConverter(filepath)()
    for key, item in JsonConv.items():
        try:
            pymodel = ItemCreateRelations(**item)
            back_item = pymodel.model_dump(exclude_unset=True)
            assert item == back_item, (f"валидация исходных данных не прошла. см. diff в лога. "
                                       f"скорее всего проблема в именах ключей или формате значений (int vs str)"
                                       f" {key}")
        except ValidationError as e:
            print("Validation errors:")
            for error in e.errors():
                print(f"  Field: {' -> '.join(str(loc) for loc in error['loc'])}")
                print(f"  Type: {error['type']}")
                print(f"  Message: {error['msg']}")
                print(f"  Input: {error['input']}")
                print()
            assert False, "Validation failed"


def test_source_constraint_data():
    """
        тестирование исходных данных на ограничение по уникальности
    """
    from app.core.utils.alchemy_utils import JsonConverter
    filepath = get_filepath_from_dir_by_name()
    JsonConv = JsonConverter(filepath)()
    drinks: dict = {}
    for n, (key, item) in enumerate(JsonConv.items()):
        try:
            if n == 1:
                jprint(item.get('drink'))
            drink = DrinkCreateRelations(**item.get('drink'))
        except ValidationError as e:
            print("Validation errors:")
            for error in e.errors():
                print(f"  Field: {' -> '.join(str(loc) for loc in error['loc'])}")
                print(f"  Type: {error['type']}")
                print(f"  Message: {error['msg']}")
                print(f"  Input: {error['input']}")
                print()
            assert False, "Validation failed"
        if drinks.get((drink.title, drink.subtitle)):
            expected_result = drinks.get((drink.title, drink.subtitle))
            assert expected_result.model_dump(exclude_unset=True) == drink.model_dump(exclude_unset=True), drink.title
        else:
            drinks[(drink.title, drink.subtitle)] = drink
    # assert False


async def test_items_direct_import_image(authenticated_client_with_db,
                                         test_db_session
                                         ):
    """
        Тестирует импорт изображений из директории
        и последующий импорт data.json c relation & image_id
        очень долгий тест
    """
    from app.mongodb.router import directprefix, prefix
    # from app.support.item.router import ItemRouter as Router
    client = authenticated_client_with_db
    # загрузка файлов из upload_dir
    response = await client.post(f'{prefix}/{directprefix}')
    assert response.status_code == 200, response.text


async def test_items_direct_import_data(authenticated_client_with_db,
                                        test_db_session
                                        ):
    """
        Тестирует импорт изображений из директории
        и последующий импорт data.json c relation & image_id
        очень долгий тест
    """
    # from app.mongodb.router import directprefix, prefix
    from app.support.item.router import ItemRouter as Router
    client = authenticated_client_with_db
    router = Router()
    prefix = router.prefix
    response = await client.post(f'{prefix}/direct')
    if response.json().get('error_nmbr', 0) > 0:
        for item in response.json().get('error'):
            try:
                model_dict = ItemCreateRelations(**item)
                back_reverse = model_dict.model_dump(exclude_unset=True)
                assert item == back_reverse
            except Exception as e:
                assert False, f'error validation error {e}'
    assert response.status_code in [200, 422], response.text

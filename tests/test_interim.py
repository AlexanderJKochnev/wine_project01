# tests/test_interim.py
"""
    тестирование всякоразного
"""

from pathlib import Path
# import pytest
from app.core.config.project_config import settings
from app.core.utils.common_utils import jprint  # NOQA: F401
from pydantic import ValidationError


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


def test_jsonconverter():
    """
    тестирует from app.core.utils.io_utils import loadJsonConverter
    тестирует исходные данные (если выбрасывает - см. diff
    """
    # from app.core.utils.io_utils import loadJsonConverter
    from app.core.utils.common_utils import get_path_to_root
    from app.core.utils.alchemy_utils import JsonConverter
    from app.support.item.schemas import ItemCreateRelations  # noqa: F401
    from app.support.drink.schemas import DrinkCreateRelations  # noqa: F401
    filename = settings.JSON_FILENAME  # имя файла для импорта
    upload_dir = settings.UPLOAD_DIR
    dirpath: Path = get_path_to_root(upload_dir)
    filepath = dirpath / filename
    if not filepath.exists():
        assert False, f'file {filename} is not exists in {upload_dir}'
    JsonConv = JsonConverter(filepath)()
    # item: dict = JsonConv.get('-OIbS7K9nu7iw-VcdHaO')  # .get('drink')
    # item: dict = JsonConv.get('-M-VI9jGOA37Fcg_feq1')  # .get('drink')
    # item: dict = JsonConv.get('-LysMchkUQcevNT2wAhG')  # .get('drink')
    # jprint(item)
    # assert False
    for key, item in JsonConv.items():
        try:
            # pymodel = DrinkCreateRelations(**item)
            pymodel = ItemCreateRelations(**item)
            back_item = pymodel.model_dump(exclude_unset=True)
            # jprint(back_item)
            # jprint(JsonConv.get('-OIbS7K9nu7iw-VcdHaO'))
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

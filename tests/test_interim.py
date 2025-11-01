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
from app.support.item.schemas import ItemCreateRelation, DrinkCreateRelation  # noqa: F401

pytestmark = pytest.mark.asyncio

trob = ["-Lymvm4_ThSSpUZ-RzFJ.png",
        "-Lyn3fPXJtUnleVAwC_V.png",
        "-Lyn77KU1LO4tcXMcPSo.png",
        "-LynA8QtpDfTRKK57ByK.png",
        "-LynGOOQFp0REbzpfUDh.png",
        "-M-B8gu3HCcEg1GsGS4w.png",
        "-M-BCjRNX51_aXLnE5Tz.png",
        "-M-BPmDfQ_6SFQt6DYDV.png",
        "-M-H-6Vqv2xyFxi9thR6.png",
        "-M-HClMqkS6-dyc4-RPb.png",
        "-M-HHyXBoDGgP56aBact.png",
        "-M-K2SvlvwyyB2iPesIP.png",
        "-M-OWs4Zsnf8gwj-inrS.png",
        "-M-OY6Esn6kDmU8-iKD1.png",
        "-M-Vv-2y2zZpLrt8UFtm.png",
        "-M-ZkvcdAWggCg5RhD_r.png",
        "-M-Zkw1F4VLAELGpjVtp.png",
        "-M-djwPhHZL0MM9ckn6t.png",
        "-M-dpHCx7YXT02Rv4a6h.png",
        "-M-dwB-70_y2cwj3zVKM.png",
        "-M-dyzI_JfxJ746M4Pg0.png",
        "-M-ff1Prk4uJ9HN5wSHi.png",
        "-M-fi8G2Ji3N-A04WBNk.png",
        "-M-nzeMiaO-_fko65t4K.png",
        "-M-omf-mviBwV14qcBXG.png",
        "-M-u2E-1hWVfklAU7LdD.png",
        "-M0HzVjRTq879OetWmGG.png",
        "-M0Sq_blYYRNNUEzKZXy.png",
        "-M0SxgOBILvEUI7kgOIX.png",
        "-M0T-dopt_b_58tXij_y.png",
        "-M0anZ356ynkzYQB0dOA.png",
        "-M0d1sj6sSGfnNQjAqY4.png",
        "-M1-pwMtIYLNPk1jpa1S.png",
        "-M1WJHPtFAOMYRr5P2ky.png",
        "-MMntnF9o5tued3eFjKw.png",
        "-MpkT2abSS0ppLuShtwB.png",
        "-MsPkbFPgweM59aiSarL.png",
        "-MsQkrd84HBBZ94nTRbR.png",
        "-MwedlcQrcJtiq-rXD1_.png",
        "-OIVS-p8nqtKnO0GzX4c.png",
        "-OIVfSO8XXgmwDbIAeer.png",
        "-OIXNXypGv_FHQWcQ3vn.png",
        "-OIXY5GhDh3aHUZ_YwBQ.png",
        "-OIXeamXbuc8d8em2Ksk.png",
        "-OI_QLGPxQvHm3KPR68z.png",
        "-OI_V8M-DD97v5QCVMuq.png",
        "-OI_bSCFgtyPRN5xqIb5.png",
        "-OIbMxlmffSsaKwddCu8.png",
        "-OIbS7K9nu7iw-VcdHaO.png",
        "-OIbYNctD-egrepFz4ER.png",
        "-OIbfLSrTlhW28GIGDCJ.png",
        "-OIbpopAiQkIQZ4gOnc5.png"
        ]


def test_get_path_to_root():
    from app.core.utils.common_utils import get_path_to_root, enum_to_camel
    from app.core.utils.io_utils import read_file_lines_stripped
    """
        тестирование функции get_path_to_root
    """
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


def test_compaire_image_json():
    """
    сравниваем список рисунков и json
    """
    from app.core.utils.io_utils import get_filepath_from_dir, readJson
    filepath = get_filepath_from_dir_by_name()
    images_file_name: list = [file.stem for file in get_filepath_from_dir()]
    json_images = list(readJson(filepath).get('items'))
    images_ommited = [img for img in images_file_name if img not in json_images]
    json_extra = [img for img in json_images if img not in images_file_name]
    print('json_extra')
    jprint(json_extra)
    print('images ommited')
    jprint(images_ommited)
    # assert False, f'{len(json_images)=}::{len(images_file_name)}'
    assert not images_ommited, images_ommited
    assert not json_extra, json_extra


def test_jsonconverter():
    """
    тестирует from app.core.utils.io_utils import loadJsonConverter
    тестирует исходные данные (если выбрасывает - см. diff
    """
    from app.core.utils.alchemy_utils import JsonConverter
    filepath = get_filepath_from_dir_by_name()
    JsonConv = JsonConverter(filepath)()
    for n, (key, item) in enumerate(JsonConv.items()):
        try:
            pymodel = ItemCreateRelation(**item)
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
    print(f'number of records is {n=}')


def test_jsonconverter2():
    """
    тестируем 'битыеэ записи
    тестирует исходные данные (если выбрасывает - см. diff)
    """
    from app.core.utils.alchemy_utils import JsonConverter
    from app.core.utils.common_utils import compare_dicts
    filepath = get_filepath_from_dir_by_name()
    shit_list = [a.rstrip('.png') for a in trob]

    JsonConv = JsonConverter(filepath)()
    temp = next(iter(JsonConv.values()))
    for n, (key, item) in enumerate(JsonConv.items()):
        if key not in shit_list:
            continue
        print('-------------------')
        diff = compare_dicts(temp, item)
        assert not diff, key


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
            drink = DrinkCreateRelation(**item.get('drink'))
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
    client = authenticated_client_with_db
    # загрузка файлов из upload_dir
    response = await client.post(f'{prefix}/{directprefix}')
    assert response.status_code == 200, response.text


async def test_items_direct_import_data(authenticated_client_with_db,
                                        test_db_session
                                        ):
    """
        тестирует метод items.direct_import_data
    """
    from app.mongodb.router import directprefix, prefix
    from app.support.item.router import ItemRouter as Router
    client = authenticated_client_with_db
    # загрузка файлов из upload_dir
    response = await client.post(f'{prefix}/{directprefix}')
    assert response.status_code == 200, response.text
    # загрузка из data.json
    router = Router()
    prefix = router.prefix
    response = await client.post(f'{prefix}/direct')
    assert response.status_code == 200, response.text
    result = response.json()
    error_nmbr = result.get('error_nmbr')
    assert error_nmbr == 0, result


def test_get_sqlalchemy_fields():
    """ тест процедуры получения полей sqlalchemy модели"""
    from sqlalchemy import ColumnElement
    from app.core.utils.alchemy_utils import get_sqlalchemy_fields
    from app.support.subregion.model import Subregion
    result = get_sqlalchemy_fields(Subregion, ['description*', '*ru', '*ion*'])
    assert isinstance(result, dict)
    for key, val in result.items():
        assert isinstance(val, ColumnElement), 'type is not ColumnElement'
        assert key == val.name


def test_pydantic_models_register():
    # from app.core.schemas.base import PYDANTIC_MODELS
    from app.core.utils.pydantic_utils import get_pyschema, pyschema_helper   # NOQA: F401
    from app.support import Category, Subcategory, Country, Region, Subregion  # NOQA: F401
    result = pyschema_helper(Subcategory, 'list', 'en')
    expected_result = 'SubcategoryListViewEn'
    assert result.__name__ == expected_result, result.__name__
    result = pyschema_helper(Category, 'list', 'en')
    expected_result = 'ListViewEn'
    assert result.__name__ == expected_result, result.__name__


def test_pyschema_list():
    """ сверяет каких pydantic схем нехватает """
    from app.core.schemas.base import PYDANTIC_MODELS
    mandatory_sets = ['Read',
                      'Create',
                      'Update',
                      'CreateRelation',
                      'ReadRelation,'
                      'CreateResponse'
                      ]
    model_list = ['Category',
                  'Country',
                  'Drink',
                  'Food',
                  'Item',
                  'Region',
                  'Subcategory',
                  'Subregion',
                  'Sweetness',
                  'Varietal']
    mandatory_schema = [f'{model}{schema}' for model in model_list for schema in mandatory_sets]
    current_schemas = [key.__name__ for key in PYDANTIC_MODELS]
    missed_schemas = [schema for schema in mandatory_schema if schema not in current_schemas]
    if missed_schemas:
        for key in missed_schemas:
            print(f'{key}')
        assert False
    assert True


def test_repository_register():
    """
    проверяем как действует регистр репозиториев
    :return:
    :rtype:
    """
    from app.core.utils.pydantic_utils import get_repo
    from app.support import Item, Subregion, Subcategory, Country
    for m, val in enumerate([Country, Item, Subregion, Subcategory]):
        name = val.__name__
        repo = get_repo(val)
        repo2 = get_repo(name)
        # for n, (key, val) in enumerate(RepositoryMeta._registry.items()):
        #     print(n, key, val)
        print(m, name, '===========')
        assert repo, f'не найден репозиторий для {name}'
        assert repo2, f'не найден репозиторий для {name} по имени'
        assert repo.__name__ == f'{val.__name__}Repository'
        assert repo == repo2, ''


def test_service_register():
    """
    проверяем как действует регистр services
    :return:
    :rtype:
    """
    from app.core.utils.pydantic_utils import get_service
    from app.core.services.service import ServiceMeta
    from app.support import (Item, Subregion, Subcategory, Country,
                             Category, Drink, Food, Region, Sweetness, Superfood, Varietal, Warehouse)
    for m, val in enumerate([Item, Subregion, Subcategory, Country,
                             Category, Drink, Food, Region, Sweetness, Superfood, Varietal, Warehouse]):
        name = val.__name__
        service = get_service(val)
        service2 = get_service(name)
        for n, (key, val1) in enumerate(ServiceMeta._registry.items()):
            print(n, key, val1)
        print(m, name, '===========')
        assert service, f'не найден service для {name}'
        assert service2, f'не найден service для {name} по имени'
        assert service.__name__ == f'{val.__name__}Service'
        assert service == service2, ''


def test_pyschema_register():
    """
    проверяем как действует регистр services
    :return:
    :rtype:
    """
    from app.core.utils.pydantic_utils import get_pyschema2
    from app.core.schemas.base import SchemaMeta
    from app.support import (Item, Subregion, Subcategory, Country,
                             Category, Drink, Food, Region, Sweetness, Superfood, Varietal, Warehouse)
    schemas = ['Read',
               'Create',
               'Update',
               'CreateRelation',
               'ReadRelation',
               'CreateResponseSchema',
               # 'ListViewRu',
               # 'ListViewFr',
               # 'ListViewEn',
               # 'DetailViewRu',
               # 'DetailViewFr',
               # 'DetailViewEn'
               ]
    models = [Subregion, Subcategory, Country, Category, Drink, Food, Region, Sweetness, Superfood, Varietal,
              Warehouse, Item]
    register = list(SchemaMeta._registry.keys())
    # direct from register
    schemas_name = [f'{model.__name__}{schema}' for model in models for schema in schemas]
    result = [name for name in schemas_name if name.lower() not in register]
    if result:
        print(len(result))
        jprint(sorted(result))
        print('--------------------')
        # jprint(sorted(register))
        assert False

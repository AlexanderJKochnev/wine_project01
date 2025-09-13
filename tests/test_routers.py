# flake8: noqa: E501
# tests/test_routers.py
""" в этой директории тесты для тестирования
    - генератора тестовых данных
    - роутеров
    - схем
    рекомендуется запускать если будут падать тесты test_create, test_patch, test_get_one, test_delete
    pytest tests/test_routers.py --tb=auto --disable-warnings -vv --capture=no
"""

import pytest
from pydantic import TypeAdapter, ValidationError
import json

pytestmark = pytest.mark.asyncio


@pytest.mark.skip
async def test_get(authenticated_client_with_db, test_db_session, fakedata_generator):
    # from app.support.drink.router import DrinkRouter as Router
    from app.support.warehouse.router import WarehouseRouter as Router
    router = Router()
    prefix = router.prefix
    # create_schema = router.create_schema
    # patch_schema = router.patch_schema
    id = 2
    client = authenticated_client_with_db
    response = await client.get(f'{prefix}/{id}')
    assert response.status_code == 200
    result = response.json()
    print(f'<<<<<{result.keys()}>>>>')
    for key, val in result.items():
        print(f'{key}: {val}')
    assert True



async def test_create_drink(authenticated_client_with_db, test_db_session):
    """
    это тест детальной обработки ошибок drink и всех связаных таблиц
    при отсутствии ошибок в тесте test_fakedata_generator запускать не требуется
    при необходимости - заменить импорт и data на то, что в ошибках выдаст test_fakedata_generator
    """
    from app.support.drink.router import DrinkRouter  # noqa: F401
    from app.support.category.router import CategoryRouter  # noqa: F401
    from app.support.country.router import CountryRouter  # noqa: F401
    from app.support.region.router import RegionRouter  # noqa: F401
    from app.support.color.router import ColorRouter  # noqa: F401
    from app.support.sweetness.router import SweetnessRouter  # noqa: F401
    from app.support.warehouse.router import WarehouseRouter  # noqa: F401
    from app.support.customer.router import CustomerRouter  # noqa: F401

    router_list = (CountryRouter, RegionRouter, CategoryRouter, ColorRouter,
                   SweetnessRouter)
    client = authenticated_client_with_db
    data = {'category': 'Wine',
            'country': 'Spain',
            'color': 'Red',
            'sweetness': 'Dry',
            'region': 'Catalonia',
            'subtitle': 'Port Steven',
            'alcohol': 7.45,
            'sugar': 0.57,
            'aging': 10,
            'sparkling': True,
            'description': 'Drug former question.'
                           'Until friend himself after level. Apply forward eye. A avoid camera hour. '
                           'National return goal former need think kind thought.',
            'description_ru': 'Agreement behavior expect positive rise institution box. '
                              'Which parent whose talk discuss care size. One poor car. '
                              'Thus election section including on.',
            'name_ru': 'Хорошее испанское вино',
            'name': 'Good spanish wine',
            # 'food': ['Ellenfurt',]
            }
    datacopy = data.copy()
    subdata: dict = {}
    for Router in router_list:
        router = Router()
        prefix = router.prefix
        create_schema = router.create_schema
        model_name: str = router.model.__name__
        if model_name:
            subdata['name'] = data.pop(model_name.lower())
            if model_name == 'Region':
                subdata['country_id'] = data.pop('country_id')
            try:
                _ = create_schema(**subdata)
            except Exception as e:
                assert False, f'ошибка валидации {model_name=}, {e}, {subdata=}'
            response = await client.post(f'{prefix}', json=subdata)
            assert response.status_code == 200, f'Ошибка create {model_name}'
            res = response.json()
            data[f'{model_name.lower()}_id'] = res['id']
            subdata = {}
    for key, val in data.items():
        # print(f'            {key}::{val}')
        pass

    router = DrinkRouter()
    prefix = router.prefix
    create_schema = router.create_schema
    try:
        _ = create_schema(**data)
    except Exception as e:
        assert False, f'Ошибка валидации Drink {e}, {data}'

    response = await client.post(f'{prefix}', json=data)
    assert response.status_code == 200

    result = response.json()
    # validate_response = create_schema(**result.model_dump())

    for key, val in datacopy.items():
        if not isinstance(result.get(key), float):
            # проверка идентичности входных значений и сохраннх данных
            # проблема - float возвращается из json() как str после округления,
            # поэтому пока нет необходимости в математической точности - не сравниваем
            assert result.get(key) == val, f'{key=} {val=} {result.get('key')=}'
    id = result.get('id')

    response = await client.get(f'{prefix}/{id}')
    assert response.status_code == 200, response.text


@pytest.mark.skip
async def test_fakedata_generator(authenticated_client_with_db, test_db_session, get_fields_type):
    client = authenticated_client_with_db
    counts = 10
    for key, val in get_fields_type.items():
        try:
            for n in range(counts):
                route = key
                if n % 2 == 1:
                    data = {k2: v2() for k2, v2 in val['required_only'].items()}
                else:
                    data = {k2: v2() for k2, v2 in val['all_fields'].items()}
                response = await client.post(f'{route}', json=data)
                assert response.status_code == 200, f'{key}::{data}'
        except Exception as he:
            # if he.status_code != 409:
            #     # logger.warning(f"HTTP error in get_one: {he.detail}")
            assert False, f'error {he=}, {response.status_code=} {key}::{data}'


@pytest.mark.skip
async def test_patch(authenticated_client_with_db, test_db_session, fakedata_generator):
    from app.support.category.router import CategoryRouter as Router
    router = Router()
    prefix = router.prefix
    # create_schema = router.create_schema
    patch_schema = router.patch_schema
    data = {'description': 'changed_Now hour institution situation. '
                           'Training heart stand adult large health risk. '
                           'Do thought personal before try letter.',
            'description_ru': 'changed_Range important several short box picture. '
                              'Executive up hold push everything hotel. Professor source threat power. '
                              'Cover my middle.',
            'name_ru': 'changed_Christopher King',
            'name': 'changed_Anna Barton'}
    try:
        _ = patch_schema(**data)  # валидация входных данных
    except Exception as e:
        assert False, f'data validation error. {e}'
    id = 1
    client = authenticated_client_with_db
    response = await client.patch(f'{prefix}/{id}', json=data)
    assert response.status_code == 200
    result = response.json()
    for key, val in data.items():
        assert result.get(key) == val


@pytest.mark.skip
async def test_greenlet(authenticated_client_with_db, test_db_session):
    """ тестирование one_to_many relationships"""
    from app.support.customer.router import CustomerRouter as RouterMain
    from app.support.warehouse.router import WarehouseRouter as RouterSlave
    client = authenticated_client_with_db
    master: dict = {'login': 'name',
                    'firstname': 'name_ru',
                    'lastname': 'last_name'}
    slave: dict = {'customer_id': 1,
                   'name': 'name'}
    router_main = RouterMain()
    router_slave = RouterSlave()
    prefix_main = router_main.prefix
    prefix_slave = router_slave.prefix
    create_master = router_main.create_schema
    create_slave = router_slave.create_schema
    count = 3
    # валидация данных :
    try:
        _ = create_master(**master)
    except Exception as e:
        assert False, f'валидация мастер не прошла {e}'
    try:
        _ = create_slave(**slave)
    except Exception as e:
        assert False, f'валидация slave не прошла {e}'
    # генератор данных master
    data_master = [{key: f'{val}_{n}' for key, val in master.items()} for n in range(count)]
    for data in data_master:
        response = await client.post(f'{prefix_main}', json=data)
        assert response.status_code == 200, f'create for data_master error {data}'
    response = await client.get(f'{prefix_main}')
    assert response.status_code == 200, 'get for data_master error'
    result = response.json()

    # генератор данных slave
    for x in result['items']:
        try:
            data = {key: f'{val}_{x['id']}' for key, val in slave.items()}
            data['customer_id'] = 1
            response = await client.post(f'{prefix_slave}', json=data)
            assert response.status_code == 200, f'create for data_slave error {data}'
        except Exception as e:
            assert False, f'{e} {data=} {x['id']=}'


@pytest.mark.skip
async def test_search(authenticated_client_with_db, test_db_session, create_drink):
    """ тестирование поиска в drink """
    from random import randint
    client = authenticated_client_with_db
    prefix = '/drinks'
    id = create_drink
    response = await client.get(f'{prefix}/{id}')
    assert response.status_code == 200, response.text
    tmp = response.json()
    data = ' '.join((val.replace('.', ' ').replace('  ', '^ ').replace('^', '')
                     for val in tmp.values() if isinstance(val, str))).split(' ')
    query = data[randint(0, len(data) - 1)]
    assert query in data, f'{query} not in record investgated'
    params = {'query': query}
    response = await client.get(f'{prefix}/search', params=params)
    assert response.status_code == 200, response.text
    result = response.json().get('items')
    resp = [item for item in result if item.get('id') == id]
    assert resp, 'поиск выполнен неверно'


async def test_new_data_generator1(authenticated_client_with_db, test_db_session):
    """ тестируем генератор тестовых данных """
    from tests.data_factory.fake_generator import generate_test_data
    from app.support.drink.router import router
    client = authenticated_client_with_db
    rout = router()
    assert True
    #csource = simple_router_list + complex_router_list
    test_number = 5     # количество записей
    for n, item in enumerate(source):
        try:
            router = item()
        except Exception as e:
            assert False, f'error {e}, {n}'
            
        schema = router.create_schema
        adapter = TypeAdapter(schema)
        prefix = router.prefix
        test_data = generate_test_data(schema, test_number, {
            'int_range': (1, 5),
            'decimal_range': (0.5, 1),
            'float_range': {'price': (50.0, 200.0)},
            # 'field_overrides': {'name': 'Special Product'},
            'faker_seed': 42})
    assert False
    



    
    router = DrinkRouter()
    schema = router.create_schema_relation
    adapter = TypeAdapter(schema)
    prefix = router.prefix
    for n, val in enumerate(new_data_generator):
        try:
            json_data = json.dumps(val)
            adapter.validate_json(json_data)
            assert True
        except ValidationError as e:
            assert False, f"Errors: {e.errors()}"
        

async def test_get_or_create(authenticated_client_with_db, test_db_session):
    from app.support.category.router import CategoryRouter
    client = authenticated_client_with_db
    router = CategoryRouter()
    create_schema = router.create_schema
    prefix = router.prefix
    data = {"name": "Design",
            "name_ru": "Заработать",
            "name_fr": "Mari",
            "description": "Cup operation discussion significant early budget parent skill. Fund admit challenge individual government. Anything school Democrat first success yet. Many well product. Another information process those again sure six care. Whose business task offer response bring enough. Begin student rock smile five note eight. Look front teach notice final.",
            "description_ru": "Зачем висеть смеяться кидать пропаганда художественный основание тусклый. Жить спалить лиловый возбуждение. Наткнуться редактор растеряться тяжелый ложиться материя. Построить наступать успокоиться. Скользить кузнец засунуть светило нервно заявление передо металл.",
            "description_fr": "Rouge mort habiter jeunesse rose. Inviter habitant feuille paix. Prière douceur angoisse moindre surveiller corps effacer sable. Sourd résoudre fou combien toit. Employer inquiétude salle tout ferme réfléchir."
            }
    try:
        _ = create_schema(**data)
    except Exception as e:
        assert False, f'Ошибка валидации данных: {e}'
    response = await client.post(f'{prefix}', json=data)
    assert response.status_code == 200, response.text
    response = await client.post(f'{prefix}', json=data)
    assert response.status_code == 200, response.text

async def test_get_relation(authenticated_client_with_db, test_db_session):
    from app.support.subregion.router import SubregionRouter as Router
    # from app.support.region.router import RegionRouter as Router
    # from app.support.country.router import CountryRouter as Router
    from app.core.utils.common_utils import get_all_dict_paths, get_nested, set_nested, pop_nested
    client = authenticated_client_with_db
    
    router = Router()
    create_schema = router.create_schema
    create_schema_relation = router.create_schema_relation
    adapter = TypeAdapter(create_schema_relation)
    prefix = router.prefix
    service = router.service
    
    data = {
    "region": {
      "country": {
        "name": "Spain",
        "name_ru": "Испания",
        "name_fr": "Espagne",
        "description": "Spain is a country in Europe known for wine.",
        "description_ru": "Испания — страна в Европе, известная своими винами.",
        "description_fr": "Espagne est un pays d'Europe réputé pour son vin."
      },
      "name": "Rioja",
      "name_ru": "Рибера-дель-Дуэро",
      "name_fr": "Rioja",
      "description": "Rioja is a wine region in Spain.",
      "description_ru": "Рибера-дель-Дуэро — винный регион в Испания.",
      "description_fr": "Rioja est une région viticole en Espagne."
    },
    "name": "Alavesa",
    "name_ru": "Алавеса",
    "name_fr": "Alavesa",
    "description": "Alavesa is a subregion of Rioja.",
    "description_ru": "Алавеса — субрегион Рибера-дель-Дуэро.",
    "description_fr": "Alavesa est un sous-région de Rioja."
    }
    # data = data.get('region')
    # data = data.get('country')
    try:
        json_data = json.dumps(data)
        adapter.validate_json(json_data)
        assert True
    except ValidationError as e:
        assert False, f"Ошибка валидации входных данных. Errors: {e.errors()}"
    main_dict = {key: service.get_model_by_name(val) for key, val in get_all_dict_paths(data).items()}
    for key, val in main_dict.items():
        subdata = pop_nested(data, key)
        try:
            _ = val(**subdata)
        except Exception as e:
            assert False, f'{e}, {key}, {json.dumps(subdata, indent=2, ensure_ascii=False)}'
        set_nested(data, f'{key}_id', 1)
    try:
        _ = create_schema(**data)
    except Exception as e:
        assert False, f'валидация поcле обновления {e}'
    response = await client.post(f'{prefix}/relation', json=data)
    assert response.status_code == 200, response.text


async def test_new_data_generator(authenticated_client_with_db, test_db_session,
                                  simple_router_list, complex_router_list):
    from tests.data_factory.fake_generator import generate_test_data
    source = simple_router_list + complex_router_list
    test_number = 10
    client = authenticated_client_with_db
    for n, item in enumerate(source):
        router = item()
        schema = router.create_schema
        adapter = TypeAdapter(schema)
        prefix = router.prefix
        test_data = generate_test_data(
            schema, test_number,
            {'int_range': (1, test_number),
             'decimal_range': (0.5, 1),
             'float_range': (0.1, 1.0),
             # 'field_overrides': {'name': 'Special Product'},
             'faker_seed': 42}
            )
        for m, data in enumerate(test_data):
            try:
                # _ = schema(**data)      # валидация данных
                json_data = json.dumps(data)
                adapter.validate_json(json_data)
                assert True
            except Exception as e:
                assert False, f'Error IN INPUT VALIDATION {e}, router {prefix}, example {m}'
            try:
                response = await client.post(f'{prefix}', json = data)
                assert response.status_code == 200, f'||{prefix}, {response.text}'
            except Exception as e:
                assert False, f'{response.status_code=} {prefix=}, error: {e}, example {m}, {response.text}'
"""
    test_data = None
    from app.support.drink.router import DrinkRouter
    router = DrinkRouter()
    schema = router.create_schema
    adapter = TypeAdapter(schema)
    prefix = router.prefix
    router = DrinkRouter()
    print("Router prefix:", router.prefix)
    print("Read schema:", router.read_schema)
    print("Fields:", list(router.read_schema.model_fields.keys()))
    test_data = [
            {"category_id": 7, "color_id": 8, "sweetness_id": 6, "subregion_id": 1, "title": "lAtsniQNBfjMJObaZvPf",
                    "title_native": None, "subtitle_native": "CBIWveRegjXaqVXLXCNi", "subtitle": None,
                    "alc": 0.36752304919533296, "sugar": 0.5806690384391704, "aging": 5, "sparkling": None,
                    "description": "MUkURnQBSKoIUZFjdyOe", "description_ru": "GvWQuoGqhsIZVdZfuBIU",
                    "description_fr": None},
            {"category_id": 2, "color_id": 3, "sweetness_id": 5, "subregion_id": 6, "title": "gfrGFTpYBwqmjvXPcFHK",
                    "title_native": "ihiYUdmfAeIVhawvVMpa", "subtitle_native": None, "subtitle": None,
                    "alc": 0.7992019667771836, "sugar": 0.8901261684051047, "aging": 9, "sparkling": None,
                    "description": "kVkrUidYLVokOpkJBjTW", "description_ru": None,
                    "description_fr": "zqMoxvsscHbEKjtXoDHN"},
            {"category_id": 6, "color_id": 9, "sweetness_id": 10, "subregion_id": 8, "title": "tKHkxjAlCKstBSgTOZOG",
                    "title_native": None, "subtitle_native": "gOJZvzmQYTucMwfCOCrk", "subtitle": "ylCotlwGzHzpCHkJydqr",
                    "alc": 0.1150442009137261, "sugar": 0.3552974891120789, "aging": 9, "sparkling": False,
                    "description": "HsOqrrbDJUicnvJVOLdB", "description_ru": None, "description_fr": None},
            {"category_id": 5, "color_id": 2, "sweetness_id": 9, "subregion_id": 7, "title": "fZabagpyCbCEMCpoeNNZ",
                    "title_native": None, "subtitle_native": None, "subtitle": "JmRJXCgxgBYbpTXEciRF",
                    "alc": 0.9914355116276414, "sugar": 0.48197031130075996, "aging": 3, "sparkling": None,
                    "description": None, "description_ru": "owRVskmBKhitkJPUuAOi", "description_fr": None},
            {"category_id": 4, "color_id": 5, "sweetness_id": 3, "subregion_id": 2, "title": "aESxrXCGsJYpADdODwxw",
                    "title_native": "ltcgYXUjYROQlYONQgON", "subtitle_native": None, "subtitle": "XccaguABxSgDezXGnUtK",
                    "alc": 0.7224170050273336, "sugar": 0.5670533699446634, "aging": 2, "sparkling": True,
                    "description": "VoHWNFeLicgyWyWsCGfg", "description_ru": "CgcqjgHHsmAIQkhJTxly",
                    "description_fr": None},
            {"category_id": 9, "color_id": 9, "sweetness_id": 4, "subregion_id": 10, "title": "eIpLVccndpTizJQqxUxm",
                    "title_native": "COlBWMqxAuqHLBinXIps", "subtitle_native": None, "subtitle": "IomEEUKQBoaPCWZOEOrf",
                    "alc": 0.5476083412256929, "sugar": 0.9768010914489466, "aging": 9, "sparkling": None,
                    "description": None, "description_ru": "JFscOVCreLoxvOsBbWzc",
                    "description_fr": "SGECwJVmbHvWBbNYBTja"},
            {"category_id": 6, "color_id": 4, "sweetness_id": 1, "subregion_id": 8, "title": "KCDJpwLrNCKQAdNmUyuK",
                    "title_native": "dxwhUsnpLKkypDxyNcMW", "subtitle_native": None, "subtitle": "oXUxKUCCXzxdPUzWJsmp",
                    "alc": 0.5130736136070028, "sugar": 0.21538321879282046, "aging": 3, "sparkling": True,
                    "description": "DRPJkASsJyWQCppDOSdz", "description_ru": None, "description_fr": None},
            {"category_id": 1, "color_id": 5, "sweetness_id": 7, "subregion_id": 7, "title": "LDaFKhttpEOPGjnUJMoo",
                    "title_native": None, "subtitle_native": None, "subtitle": "mivbqKKdapYwJMAFlHwm",
                    "alc": 0.12103160652804867, "sugar": 0.5638407683961387, "aging": 3, "sparkling": False,
                    "description": None, "description_ru": None, "description_fr": None},
            {"category_id": 10, "color_id": 8, "sweetness_id": 6, "subregion_id": 3, "title": "gVmbNOThRUKdgHjTSGfv",
                    "title_native": None, "subtitle_native": None, "subtitle": None, "alc": 0.1322944331451323,
                    "sugar": 0.20382409973454954, "aging": 4, "sparkling": None, "description": "sROGtQCmWfINmpRmJxrB",
                    "description_ru": None, "description_fr": None},
            {"category_id": 5, "color_id": 3, "sweetness_id": 8, "subregion_id": 3, "title": "SgNwZuqBliFkEpfwMsfX",
                    "title_native": None, "subtitle_native": "OxUydQyYwWrxcouHUkMp", "subtitle": "OOGAcVyuQjRqryPPmYEk",
                    "alc": 0.6202312364007778, "sugar": 0.8523281980791738, "aging": 3, "sparkling": True,
                    "description": None, "description_ru": "pBJCYUfodMHHdjcxthaH",
                    "description_fr": "lfjdfusQvcSBiuAqFAIY"}
            ]
    for n, data in enumerate(test_data):
        try:
            # _ = schema(**data)      # валидация данных
            json_data = json.dumps(data)
            adapter.validate_json(json_data)
            assert True
        except Exception as e:
            assert False, f'input validation error {e}, router {prefix}, example {n}'
        try:
            response = await client.post(f'{prefix}', json = data)
            assert response.status_code == 200, f'{response.text}'
        except Exception as e:
            assert False, f'example {n}, prefix {prefix}, {response.status_code=}, {response.text}'
"""
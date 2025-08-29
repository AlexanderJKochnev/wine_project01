# tests/test_routers.py
""" в этой директории тесты для тестирования
    - генератора тестовых данных
    - роутеров
    - схем
    рекомендуется запускать если будут падать тесты test_create, test_patch, test_get_one, test_delete
    pytest tests/test_routers.py --tb=auto --disable-warnings -vv --capture=no
"""

import pytest

pytestmark = pytest.mark.asyncio


async def test_get(authenticated_client_with_db, test_db_session, fakedata_generator):
    from app.support.region.router import RegionRouter as Router
    router = Router()
    prefix = router.prefix
    # create_schema = router.create_schema
    # patch_schema = router.patch_schema
    id = 2
    client = authenticated_client_with_db
    response = await client.get(f'{prefix}/{id}')
    assert response.status_code == 200
    result = response.json()
    print(f'====={result.keys()}=====')
    for key, val in result.items():
        print(f'{key}: {val}')
    assert True

@pytest.mark.skip
async def test_create(authenticated_client_with_db, test_db_session):
    """
    это тест детальной обработк ошибок теста test_fakedata_generator
    при отсутствии ошибок в тесте test_fakedata_generator запускать не требуется
    при необходимости - заменить импорт и data на то, что в ошибках выдаст test_fakedata_generator
    """
    from app.support.drink.router import DrinkRouter as Router
    router = Router()
    prefix = router.prefix
    create_schema = router.create_schema
    data = {'category_id': 1,
            'food_id': 1,
            'color_id': 1,
            'sweetness_id': 1,
            'region_id': 1,
            'subtitle': 'Port Steven',
            'alcohol': 7.45,
            'sugar': 0.57,
            'aging': 'Codymouth',
            'sparkling': True,
            'description': 'Drug former question.'
                           'Until friend himself after level. Apply forward eye. A avoid camera hour. '
                           'National return goal former need think kind thought.',
            'description_ru': 'Agreement behavior expect positive rise institution box. '
                              'Which parent whose talk discuss care size. One poor car. '
                              'Thus election section including on.',
            'name_ru': 'Michael Moore',
            'name': 'Tyler Woods'}
    try:
        _ = create_schema(**data)  # валидация входных данных
    except Exception as e:
        assert False, f'data validationi error. {e}'
    client = authenticated_client_with_db
    response = await client.post(f'{prefix}', json=data)
    assert response.status_code == 200
    result = response.json()
    for key, val in data.items():
        assert result.get(key) == val


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

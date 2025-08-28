# tests/test_routers.py
""" в этой директории тесты для тестирования
    - генератора тестовых данных
    - роутеров
    - схем
    рекомендуется запускать если будут падать тесты test_create, test_update, test_get_one, test_delete
    pytest tests/test_routers.py --tb=auto --disable-warnings -vv --capture=no
"""

import pytest

pytestmark = pytest.mark.asyncio


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


async def test_update(authenticated_client_with_db, test_db_session, fakedata_generator):
    from app.support.category.router import CategoryRouter as Router
    router = Router()
    prefix = router.prefix
    create_schema = router.create_schema
    update_schema = router.update_schema
    data = {'name': 'updated_name', 'name_ru': 'новое имя'}
    try:
        _ = create_schema(**data)  # валидация входных данных
    except Exception as e:
        assert False, f'data validation error. {e}'
"""
    client = authenticated_client_with_db
    response = await client.post(f'{prefix}', json = data)
    assert response.status_code == 200
    result = response.json()
    for key, val in data.items():
        assert result.get(key) == val
"""

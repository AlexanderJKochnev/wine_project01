# tests/test_preact.py
"""
    тестируем методы preact/delete
"""

from typing import Any, Dict, List  # NOQA: F401

import pytest
from sqlalchemy import and_, func, or_, select, sql  # NOQA: F401

from app.core.utils.common_utils import jprint  # NOQA: F401

pytestmark = pytest.mark.asyncio


async def test_create_routers(authenticated_client_with_db, test_db_session):
    """
        тестируем роутеры CREATE
    """
    from app.preact.create.router import CreateRouter
    from tests.data_factory.fake_generator import generate_test_data
    client = authenticated_client_with_db
    router = CreateRouter()
    prefix = router.prefix
    test_number = 5
    sucess_pref = []
    for pref, model in router.source.items():
        schema = router.__get_schemas__(model)
        test_data = generate_test_data(schema,
                                       test_number,
                                       {'int_range': (1, test_number),
                                        'decimal_range': (0.5, 1),
                                        'float_range': (0.1, 1.0),
                                        'faker_seed': 42})
        for m, data in enumerate(test_data):
            # валидация
            py_model = schema(**data)
            rev_dict = py_model.model_dump()
            assert data == rev_dict, f'pydantic validation fault "{pref}"'
            path = f'{prefix}/{pref}'
            response = await client.post(path, json=data)
            if response.status_code not in [200, 201]:
                jprint(data)
                print(f'----------{path}---------------')
                jprint(sucess_pref)
            assert response.status_code in [200, 201], f'{path} {m}'
        sucess_pref.append((pref, m))


async def test_get_routers(authenticated_client_with_db, test_db_session):
    """  тесты GET """
    from app.preact.get.router import GetRouter
    client = authenticated_client_with_db
    router = GetRouter()
    id = 3   # ищем первую запись
    prefix = router.prefix
    subprefix = [key for key, val in router.source.items()]
    language = ['ru', 'en', 'fr']
    test_set = [f'{prefix}/{a}/{b}' for a in subprefix for b in language]
    for pref in test_set:
        pre = f'{pref}/{id}'
        response = await client.get(pre)
        assert response.status_code == 200, f'{pre=}  {response.text}'
        result = response.json()
        assert isinstance(result, dict), result
        assert result['id'] == id, f"ожидалась запись {id=}, получена id = {result['id']}"


async def test_read_routers(authenticated_client_with_db, test_db_session):
    """  тесты GET """
    from app.preact.read.router import ReadRouter
    client = authenticated_client_with_db
    router = ReadRouter()
    id = 3   # ищем первую запись
    prefix = router.prefix
    subprefix = [key for key, val in router.source.items()]
    # language = ['ru', 'en', 'fr']
    test_set = [f'{prefix}/{a}' for a in subprefix]
    for pref in test_set:
        pre = f'{pref}/{id}'
        response = await client.get(pre)
        assert response.status_code == 200, f'{pre=}  {response.text}'
        result = response.json()
        assert isinstance(result, dict), result


async def test_patch_routers(authenticated_client_with_db, test_db_session):
    """ тестирование route PATCH """
    from app.preact.read.router import ReadRouter
    from app.preact.patch.router import PatchRouter
    client = authenticated_client_with_db
    router = ReadRouter()
    router2 = PatchRouter()
    id = 2   # ищем запись
    prefix = router.prefix
    prefix2 = router2.prefix
    subprefix = [key for key, val in router2.source.items()]
    test_set = [f'{a}' for a in subprefix]
    for pref in test_set:
        # получение записи
        get_prefix = f'{prefix}/{pref}/{id}'
        response = await client.get(get_prefix)
        assert response.status_code == 200, f'{get_prefix}. запись {id=} не существует'
        result = response.json()
        # генерируем измененния в текстовых полях
        expected_data = 'updated_data'
        data = {key: expected_data for key, val in result.items() if isinstance(val, str)}
        # запускаем изменение
        full_prefix = f'{prefix2}/{pref}/{id}'
        response = await client.patch(full_prefix, json=data)
        assert response.status_code == 200, f'{full_prefix}'
        result = response.json()
        for key, val in data.items():
            assert result.get(key) == val, f'update fault. full_prefix. {key}'


async def test_handbooks_routers(authenticated_client_with_db, test_db_session,
                                 routers_get):
    from app.preact.handbook.router import HandbookRouter
    client = authenticated_client_with_db
    router = HandbookRouter()
    prefix = router.prefix
    subprefix = [key for key, val in router.source.items()]
    language = ['ru', 'en', 'fr']
    test_set = [f'{prefix}/{a}/{b}' for a in subprefix for b in language]
    for pref in test_set:
        pre = f'{pref}'
        response = await client.get(pre)
        assert response.status_code == 200, f'{pre=}  {response.text}'
        result = response.json()
        assert isinstance(result, List), result


async def test_delete_routers(authenticated_client_with_db, test_db_session):
    """  тестирование роутера DELETE """
    from app.preact.delete.router import DeleteRouter
    client = authenticated_client_with_db
    router = DeleteRouter()
    prefix = router.prefix
    id = 1   # удаляем первую запись
    for pref, model in reversed(router.source.items()):

        full_prefix = f'{prefix}/{pref}'
        print(f'========={full_prefix}')
        response = await client.delete(f'{full_prefix}/{id}')
        assert response.status_code == 200, f'{full_prefix}/{id}, {response.text}'
        result = response.json()
        assert result.get('success'), f'{full_prefix}/{id} :: {result}'

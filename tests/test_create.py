# tests/test_create.py
"""
проверка методов post c валидацией входящих и исходящих данных
"""

import pytest
from pydantic import TypeAdapter
import json
from app.core.utils.common_utils import jprint
pytestmark = pytest.mark.asyncio


async def test_new_data_generator(authenticated_client_with_db, test_db_session,
                                  simple_router_list, complex_router_list):
    """ валидация генерируемых данных и загрузка """
    from tests.data_factory.fake_generator import generate_test_data
    source = simple_router_list + complex_router_list
    test_number = 1
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
                # print(json.dumps(data, indent = 2, ensure_ascii = False))
                # _ = schema(**data)      # валидация данных
                json_data = json.dumps(data)
                adapter.validate_json(json_data)
                assert True
            except Exception:
                # assert False, f'Error IN INPUT VALIDATION {e}, router {prefix}, example {m}'
                assert False, f'validation false {data=}'
            try:
                response = await client.post(f'{prefix}', json=data)
                assert response.status_code in [200, 201], f'{prefix}, {response.text}'
            except Exception as e:
                assert False, f'{response.status_code=} {prefix=}, error: {e}, example {m}, {response.text}'


async def test_new_data_generator_relation(authenticated_client_with_db, test_db_session,
                                           simple_router_list, complex_router_list):
    """ валидация генерируемых данных со связанными полями и загрузка """
    from tests.data_factory.fake_generator import generate_test_data
    source = simple_router_list + complex_router_list
    test_number = 1
    client = authenticated_client_with_db
    for n, item in enumerate(source):
        router = item()
        schema = router.create_schema_relation
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
                response = await client.post(f'{prefix}/hierarchy', json=data)
                assert response.status_code in [200, 201], f'{prefix}, {response.text}'
            except Exception as e:
                jprint(data)
                assert False, f'{e} {response.status_code} {prefix=}, {response.text}'

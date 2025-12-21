# tests/test_fucking_drink.py
"""
проверка методов для долбаного drinks
"""

import pytest
# import json
# from app.core.utils.common_utils import jprint
pytestmark = pytest.mark.asyncio


@pytest.mark.skip
async def test_new_drink_data_generator(authenticated_client_with_db, test_db_session,
                                        simple_router_list, complex_router_list):
    """ валидация генерируемых данных и загрузка """
    from tests.data_factory.fake_generator import generate_test_data
    from app.support.drink.router import DrinkRouter as Router
    test_number = 10
    # client = authenticated_client_with_db
    router = Router()
    schema = router.create_schema
    # adapter = TypeAdapter(schema)
    model = router.model
    # prefix = router.prefix
    test_data = generate_test_data(schema,
                                   test_number,
                                   {'int_range': (1, test_number),
                                    'decimal_range': (0.5, 1),
                                    'float_range': (0.1, 1.0),
                                    # 'field_overrides': {'name': 'Special Product'},
                                    'faker_seed': 42})
    for m, data in enumerate(test_data):
        # валидируем по Pydantic схеме
        py_model = schema(**data)
        rev_dict = py_model.model_dump()
        assert data == rev_dict, 'pydantic validation fault'
        # валидируем по Alchemy model
        al_model = model(**data)
        rev_dict = al_model.to_dict()
        for key in ['updated_at', 'id', 'created_at']:
            rev_dict.pop(key, None)
        assert data == rev_dict
        # response = await client.post(f'{prefix}', json=data)
        # assert response.status_code in [200, 201], f'{prefix}, {response.text}'


@pytest.mark.skip
async def test_new_drink_data_relation(authenticated_client_with_db, test_db_session):
    """ валидация генерируемых данных и загрузка """
    from tests.data_factory.fake_generator import generate_test_data
    from app.support.drink.router import DrinkRouter as Router
    test_number = 10
    client = authenticated_client_with_db
    router = Router()
    # schema = router.create_schema
    schema = router.create_schema_relation
    prefix = router.prefix
    test_data = generate_test_data(schema,
                                   test_number,
                                   {'int_range': (1, test_number),
                                    'decimal_range': (0.5, 1),
                                    'float_range': (0.1, 1.0),
                                    # 'field_overrides': {'name': 'Special Product'},
                                    'faker_seed': 42})
    for m, data in enumerate(test_data):
        # валидируем по Pydantic схеме
        py_model = schema(**data)
        rev_dict = py_model.model_dump()
        assert data == rev_dict, 'pydantic validation fault'
        response = await client.post(f'{prefix}/hierarchy', json=data)
        assert response.status_code in [200, 201], f'{prefix}/hierarchy, {response.text}'


@pytest.mark.skip
async def test_new_item_data_relation(authenticated_client_with_db, test_db_session):
    """ валидация генерируемых данных и загрузка """
    from tests.data_factory.fake_generator import generate_test_data
    from app.support.item.router import ItemRouter as Router
    test_number = 10
    client = authenticated_client_with_db
    router = Router()
    # schema = router.create_schema
    schema = router.create_schema_relation
    prefix = router.prefix
    test_data = generate_test_data(schema,
                                   test_number,
                                   {'int_range': (1, test_number),
                                    'decimal_range': (0.5, 1),
                                    'float_range': (0.1, 1.0),
                                    # 'field_overrides': {'name': 'Special Product'},
                                    'faker_seed': 42})
    for m, data in enumerate(test_data):
        # валидируем по Pydantic схеме
        py_model = schema(**data)
        rev_dict = py_model.model_dump()
        assert data == rev_dict, 'pydantic validation fault'
        response = await client.post(f'{prefix}/hierarchy', json=data)
        assert response.status_code in [200, 201], f'{prefix}/hierarchy, {response.text}'

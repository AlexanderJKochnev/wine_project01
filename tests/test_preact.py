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
    from app.preact.create.router import CreateRouter
    from tests.data_factory.fake_generator import generate_test_data
    client = authenticated_client_with_db
    router = CreateRouter()
    prefix = router.prefix
    test_number = 5
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
            response = await client.post(f'/{prefix}/{pref}', json=data)
            if response.status_code not in [200, 201]:
                jprint(data)
                print('-------------------------------')
            assert response.status_code in [200, 201], f'{pref} {m}'


async def test_delete_routers(authenticated_client_with_db, test_db_session):
    """  запускаем после test_create_routers """
    from app.preact.delete.router import DeleteRouter
    client = authenticated_client_with_db
    router = DeleteRouter()
    prefix = router.prefix
    id = 1   # удаляем первую запись
    for pref, model in reversed(router.source.items()):
        # schema = router.__get_schemas__(model)
        full_prefix = f'{prefix}/{pref}'
        response = await client.delete(f'{full_prefix}/{id}')
        assert response.status_code == 200, f'{full_prefix}/{id}'
        result = response.json()
        assert result.get('success'), f'{full_prefix}/{id} :: {result}'

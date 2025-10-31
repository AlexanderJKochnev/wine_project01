# tests/test_patch.py
"""
    тестируем все методы POST и UPDATE ()
    новые методы добавляются автоматически
    pytest tests/test_patch.py --tb=auto --disable-warnings -vv --capture=no
"""
import pytest
from app.core.utils.common_utils import jprint

pytestmark = pytest.mark.asyncio


async def test_patch_success(authenticated_client_with_db, test_db_session,
                             simple_router_list, complex_router_list, fakedata_generator):
    """ тестирует методы PATCH (patch) - c проверкой id """
    client = authenticated_client_with_db
    routers = simple_router_list + complex_router_list
    test_data: dict = {'name': 'updated_name', 'description': 'updated description',
                       'name_ru': 'обновленные данные', 'description_ru': 'обновленные данные'
                       }
    drink_data: dict = {'description': 'updated description', 'title': 'updated_name',
                        'description_ru': 'обновленные данные',
                        'title_ru': 'обновленные данные'}
    item_data: dict = {'vol': 1.0,
                       'price': 0.99}
    customer_data: dict = {'login': 'test_data',
                           'firstname': 'test_data'}
    item_id = 1
    for router_class in routers:
        router = router_class()
        prefix = router.prefix
        if prefix == '/drinks':
            source = drink_data
        if prefix == '/items':
            source = item_data
        if prefix == '/customers':
            source = customer_data
        else:
            source = test_data
        response = await client.patch(f"{prefix}/{item_id}", json=source)
        # Assert
        if response.status_code != 200:
            print(f'====={prefix}====={item_id}===')
            jprint(source)
        assert response.status_code == 200, response.text
        response_data = response.json()
        assert response_data["id"] == item_id
        for key, val in source.items():
            assert response_data[key] == val, f'{response_data[key]} != {val}'

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
    """
        тестирует методы PATCH (patch) - c проверкой id
        доделать
    """
    client = authenticated_client_with_db
    routers = simple_router_list + complex_router_list
    test_data: dict = {'name': 'updated_name', 'description': 'updated description',
                       'name_ru': 'обновленные данные', 'description_ru': 'обновленные данные'
                       }
    drink_data: dict = {'description': 'updated description', 'title': 'updated_title',
                        'description_ru': 'обновленные данные',
                        'title_ru': 'обновленные данные title'}
    item_data: dict = {'vol': 1.0,
                       # 'price': 1.0,   # this field is muted in read_relation schema
                       'image_id': 'image_pathe updated'}
    customer_data: dict = {'login': 'test_data',
                           'firstname': 'test_data'}
    item_id = 1
    for router_class in routers:
        router = router_class()
        prefix = router.prefix
        # read_schema_relations = router.read_schema_relation
        if prefix == '/drinks':
            source = drink_data
        elif prefix == '/items':
            source = item_data
        elif prefix == '/customers':
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
            if response_data.get(key) != val:
                jprint(response_data)
            assert response_data.get(key) == val, f'{prefix=}, {key=}, {val=} {response_data.get(key)=}'


async def test_patch_success2(authenticated_client_with_db, test_db_session,
                              simple_router_list, complex_router_list, fakedata_generator):
    """
        тестирует методы PATCH (patch) - c проверкой id
    """
    client = authenticated_client_with_db
    routers = simple_router_list + complex_router_list
    for router_class in routers:
        router = router_class()
        prefix = router.prefix
        if prefix in ['/api']:  # api не имеет метода all, удалить когда заведется
            continue
        response = await client.get(f'{prefix}/all')
        if response.status_code != 200:
            print(response.text)
        assert response.status_code == 200, f'{prefix=}, {response.text}'
        interim_result = response.json()
        assert isinstance(interim_result, list), f'{prefix=}, неверный результат метода get_all'
        origin_dict = interim_result[-1]
        id = origin_dict.pop('id', None)
        if id is None:
            jprint(origin_dict)
        assert id is not None, f'{prefix=}, неверный результат метода get_all - отсутвует id'
        updated_dict = {key: f'updated {val}' for key, val in origin_dict.items() if isinstance(val, str)}
        response = await client.patch(f"{prefix}/{id}", json=updated_dict)
        if response.status_code != 200:
            print(response.text)
        assert response.status_code == 200, f'{prefix=} ошибка обновления'

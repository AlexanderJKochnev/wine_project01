# tests/test_patch.py
"""
    тестируем все методы POST и UPDATE ()
    новые методы добавляются автоматически
    pytest tests/test_patch.py --tb=auto --disable-warnings -vv --capture=no
"""

import pytest
from app.core.schemas.base import ListResponse

pytestmark = pytest.mark.asyncio


async def test_patch(authenticated_client_with_db, test_db_session,
                     routers_get_all, fakedata_generator):
    """ тестирует методы PATCH (patch) - c проверкой id """
    client = authenticated_client_with_db
    routers = routers_get_all
    response_keys = ListResponse.model_fields.keys()
    # all foireign field name add to remove list
    remove_list: tuple = ('id', 'created_at', 'updated_at', 'country', 'customer')
    for prefix in routers:
        if prefix == '/drinks':
            continue
        response = await client.get(f'{prefix}')
        assert response.status_code == 200, 'метод GET не работает для пути "{prefix}"'
        assert response.json().keys() == response_keys, 'метод GET для пути "{prefix}" возвращает некорректные данные'
        tmp = response.json()
        total = len(tmp['items'])
        if total > 0:       # записи есть
            instance = tmp['items'][-1]
            id = instance['id']
            for key, val in instance.items():  # изменяем
                if isinstance(val, str):
                    instance[key] = f'changed_{val}'
                else:
                    instance[key] = None
            for x in remove_list:  # удаляем pk и
                instance.pop(x, None)
            instance_patchd = {key: val for key, val in instance.items() if val}
            resp = await client.patch(f'{prefix}/{id}', json=instance_patchd)
            assert resp.status_code == 200, f'{instance_patchd=}, {prefix}'
            result = resp.json()
            for key, val in instance_patchd.items():
                assert result.get(key) == val, f'{prefix=}, {result=} {instance_patchd=}'
        else:
            assert False, 'генератор тестовых данных не сработал на {prefix}. см. test_routers.py'

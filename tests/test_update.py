# tests/test_update.py
"""
    тестируем все методы POST и UPDATE ()
    новые методы добавляются автоматически
    pytest tests/test_update.py --tb=auto --disable-warnings -vv --capture=no
"""

import pytest
from app.core.schemas.base import ListResponse

pytestmark = pytest.mark.asyncio


async def test_patch(authenticated_client_with_db, test_db_session,
                     routers_get_all, fakedata_generator):
    """ тестирует методы PATCH (update) - c проверкой id """
    client = authenticated_client_with_db
    routers = routers_get_all
    x = ListResponse.model_fields.keys()
    for prefix in routers:
        if prefix == '/drinks':
            continue
        response = await client.get(f'{prefix}')
        assert response.status_code == 200, 'метод GET не работает для пути "{prefix}"'
        assert response.json().keys() == x, 'метод GET для пути "{prefix}" возвращает некорректные данные'
        tmp = response.json()
        total = len(tmp['items'])
        if total > 0:       # записи есть
            id = 2  # берем первую
            instance = tmp['items'][id - 1]
            for key, val in instance.items():
                print(f'==SOURCE======={key}: {val}')
            for key, val in instance.items():  # изменяем
                if isinstance(val, str):
                    instance[key] = f'changed_{val}'
                else:
                    instance[key] = None
            remove_list: tuple = ('id', 'created_at', 'updated_at')
            for x in remove_list:  # удаляем pk и
                instance.pop(x, None)
            instance_updated = {key: val for key, val in instance.items() if val}
            for key, val in instance_updated.items():
                print(f'==RESULT==={id}===={key}: {val}')
            resp = await client.get(f'{prefix}/{id}, json=instance_updated')
            assert resp.status_code == 200, f'{instance_updated=}, {prefix}'
            result = resp.json()
            for key, val in instance_updated.items():
                assert result.get(key) == val
        else:
            assert False, 'генератор тестовых данных не сработал на {prefix}. см. test_routers.py'

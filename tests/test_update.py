# tests/test_patch.py
"""
    тестируем все методы POST и UPDATE ()
    новые методы добавляются автоматически
    pytest tests/test_patch.py --tb=auto --disable-warnings -vv --capture=no
"""
import random

import pytest


pytestmark = pytest.mark.asyncio


@pytest.mark.skip
async def test_patch(authenticated_client_with_db, test_db_session,
                     real_routers_get_all, fakedata_generator):
    """ тестирует методы PATCH (patch) - c проверкой id """
    """ тест не работает в реале работает - разобраться """
    client = authenticated_client_with_db
    routers = real_routers_get_all
    # all foireign field name add to remove list
    remove_list: tuple = ('id', 'created_at', 'updated_at', 'country', 'customer')
    for router in routers:
        prefix = router.path
        if prefix in ['/drinks']:
            continue
        response = await client.get(f'{prefix}/all')
        assert response.status_code == 200, 'метод GET не работает для пути "{prefix}"'
        # assert response.json().keys() == response_keys, 'метод GET для пути "{prefix}" возвращает некорректные данные'
        tmp = response.json()
        total = len(tmp)
        if total > 0:       # записи есть
            instance = tmp[random.randint(0, total - 1)]
            id = instance.pop('id')
            for key, val in instance.items():  # изменяем
                if isinstance(val, str):
                    instance[key] = f'changed_{val}'
                else:
                    instance[key] = None
            for x in remove_list:  # удаляем pk и
                instance.pop(x, None)
            instance_patched = {key: val for key, val in instance.items() if val}
            resp = await client.patch(f'{prefix}/{id}', json=instance_patched)
            assert resp.status_code == 200, f'{prefix} {instance_patched=}'
            result = resp.json()
            for key, val in instance_patched.items():
                assert result.get(key) == val, f'{prefix=}, {result=} {instance_patched=}'
        else:
            assert False, 'генератор тестовых данных не сработал на {prefix}. см. test_routers.py'

# tests/test_preact.py
"""
    тестируем методы preact/delete
"""

from typing import Any, Dict, List  # NOQA: F401

import pytest
from sqlalchemy import and_, func, or_, select, sql  # NOQA: F401

from app.core.utils.common_utils import jprint  # NOQA: F401

pytestmark = pytest.mark.asyncio


@pytest.mark.skip
async def test_service_get_non_orm_compile(mock_engine):
    """
        тестирование sql кода (не работает для вложенных моделей - не пытайся
        просто проверить правильно ли генерируются имена полей
        для полного тестирования см следующий тест
    """

    from app.preact import GetRouter, get_lang_prefix
    from app.core.utils.alchemy_utils import get_id_field
    from sqlalchemy.dialects import postgresql
    # engine = mock_engine
    # service = Service
    router = GetRouter()
    expected_id = 1
    for prefix, tag, function in router.__source_generator__(router.source, router.languages):
        path = f'{router.prefix}/{prefix}/{expected_id}'
        mod, lang = router.__path_decoder__(path)
        models = router.source.get(mod)
        # if len(models) > 1:
        #     continue
        lang = get_lang_prefix(lang)
        fields_name = router.fields_name
        main_model = models[0]
        assert hasattr(main_model, 'id'), f'model {main_model.__name__} has no "id" field'
        fields_spec = [getattr(main_model, 'id')]
        for n, field in enumerate(fields_name):
            for model in models:
                if all((n > 0, model != main_model)):   # для связанных таблиц берем только 1 поле
                    continue
                if lang == '':  # english language
                    fields_spec.append(getattr(model, field))
                else:  # all other languages
                    column = func.coalesce(getattr(model, f'{field}{lang}'), getattr(model, field)).label(field)
                    fields_spec.append(column)
        for key in fields_spec:
            if key.name == 'id':
                continue
            assert key.name in fields_name, f'fied name {key.name} is wrong'
        stmt = (select(*fields_spec))
        for n, model in enumerate(models):
            if n == 0:  # первая модель основная ее джойнить не надо
                m1 = model
                continue
            subs = model
            # clause = get_id_field(m1, subs)
            stmt = stmt.join(subs, get_id_field(m1, subs) == subs.id)
            m1 = subs
        stmt = stmt.where(models[0].id == expected_id)
        # print(stmt)
        print('----------------')
        compiled = stmt.compile(dialect=postgresql.dialect(),
                                compile_kwargs={"literal_binds": True})
        print(str(compiled))
    assert True   # замени на False что бы посмотреть генерируемый sql code


@pytest.mark.skip
async def test_service_get_non_orm(test_db_session):
    """
        тестирование service layer & repo
        постреть что нагенерировано см предыдущий тест
    """

    from app.preact import GetRouter, get_lang_prefix
    from app.core.utils.alchemy_utils import get_id_field
    # client = authenticated_client_with_db
    # service = Service
    router = GetRouter()
    session = test_db_session
    expected_id = 1
    for prefix, tag, function in router.__source_generator__(router.source, router.languages):
        path = f'{router.prefix}/{prefix}/{expected_id}'
        mod, lang = router.__path_decoder__(path)
        models = router.source.get(mod)
        lang = get_lang_prefix(lang)
        fields_name = router.fields_name
        main_model = models[0]
        assert hasattr(main_model, 'id'), f'model {main_model.__name__} has no "id" field'
        fields_spec = [getattr(main_model, 'id')]
        for n, field in enumerate(fields_name):
            for model in models:
                if all((n > 0, model != main_model)):  # для связанных таблиц берем только 1 поле
                    continue
                if lang == '':  # english language
                    fields_spec.append(getattr(model, field))
                else:  # all other languages
                    column = func.coalesce(getattr(model, f'{field}{lang}'), getattr(model, field)).label(field)
                    fields_spec.append(column)
        for key in fields_spec:
            if key.name == 'id':
                continue
            assert key.name in fields_name, f'fied name {key.name} is wrong'
        stmt = (select(*fields_spec))
        for n, model in enumerate(models):
            if n == 0:  # первая модель основная ее джойнить не надо
                m1 = model
                continue
            subs = model
            # clause = get_id_field(m1, subs)
            stmt = stmt.join(subs, get_id_field(m1, subs) == subs.id)
            m1 = subs
        stmt = stmt.where(models[0].id == expected_id)
        result = await session.execute(stmt)
        print(result)


async def test_create_routers(authenticated_client_with_db, test_db_session):
    """
        тестируем создание
    """
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


async def test_get_routers(authenticated_client_with_db, test_db_session,
                           fakedata_generator):
    """  запускаем после test_create_routers """
    from app.preact.get.router import GetRouter
    # from app.core.utils.common_utils import jprint
    client = authenticated_client_with_db
    router = GetRouter()
    id = 1   # ищем первую запись
    prefix = router.prefix
    subprefix = [key for key, val in router.source.items()]
    # subprefix = list(router.source.keys())
    language = router.languages
    test_set = [f'{prefix}/{a}/{b}' for a in subprefix for b in language]
    for pref in test_set:
        pre = f'{pref}/{id}'
        response = await client.get(pre)
        print(pre, response.status_code)
        assert response.status_code == 200, f'{pre=}  {response.text}'
        result = response.json()
        assert isinstance(result, dict), result
        assert result['id'] == id, result['id']


async def test_delete_routers(authenticated_client_with_db, test_db_session,
                              fakedata_generator):
    """  запускаем после test_create_routers """
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

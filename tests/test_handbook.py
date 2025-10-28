# tests/test_preact.py
"""
    тестируем все методы preact
"""

# from collections import Counter
from typing import Any, Dict, List  # NOQA: F401

import pytest
from sqlalchemy import and_, func, or_, select, sql  # NOQA: F401

from app.core.utils.common_utils import jprint  # NOQA: F401

pytestmark = pytest.mark.asyncio


def test_joiner():
    from app.core.utils.common_utils import joiner
    source = ['afrika', None, 'South Amerika', None]
    joint = '. '
    expected_result = joint.join((val for val in source if val))
    print(expected_result)
    result = joiner(joint, *source)
    print(result)
    assert expected_result == result


def test_sorter():
    from app.core.utils.common_utils import dict_sorter
    source = {14: "Scotland. Highland",
              35: "France. Pouilly-Fume",
              37: "Italy. Veneto",
              48: "Greece. Drama P.G.I.",
              49: "Argentina. Mendoza",
              50: "South Africa. Paarl",
              51: "France. Chateauneuf-Du-Pape. Rhone",
              52: "Italy. The Valdobbiadene Hills",
              53: "Italy. Valdobbiadene. Cartizze",
              54: "Scotland",
              55: "France. Chablis. Grand Cru, Bougros",
              56: "Italy. Piedmont. Langhe",
              57: "Portugal. Douro Valley"}
    expected_result = dict(sorted(source.items(), key=lambda item: item[1]))
    result = dict_sorter(source)
    assert expected_result == result


def test_model_naming():
    from app.support.subcategory.model import Subcategory
    from app.support.category.model import Category
    from app.core.utils.alchemy_utils import field_naming, get_id_field
    # проверка field_naming
    result = field_naming(Category)
    exp_res = 'category_id'
    assert result == exp_res, f'field_naming работает некорректно {result} вместо {exp_res}'
    # проверка get_id_field
    result = get_id_field(Subcategory, Category)
    exp_res = Subcategory.category_id
    assert result == exp_res, f'get_id_field работает некорректно {result} вместо {exp_res}'


def test_handbook_router():
    """
    тестирует генераторы роутеров
    :return:
    :rtype:
    """
    from app.preact.handbook import HandbookRouter
    router = HandbookRouter()
    # тест __source_generator__
    print(router.languages)
    for prefix, response_model in router.__source_generator__(router.source, router.languages):
        print(f'{prefix=}, {response_model.__name__=}')
        assert isinstance(prefix, str), 'тест __source_generator__ не прошел. 1'
        # assert isinstance(tag, list), f'тест __source_generator__ не прошел - 2 элемент не лист, а {type(tag)}'
    sources = {'/some/path/en': ('path', 'en'),
               '/path/en': ('path', 'en')}
    for source, expectation in sources.items():
        result = router.__path_decoder__(source)
        print(result)
        assert result == expectation, f'(__path_decoder__ test fault, {result}'
    # assert False


async def test_handbooks_routers(authenticated_client_with_db, test_db_session,
                                 fakedata_generator, routers_get):
    """
        тестирует сгененированные рутеры
    """
    client = authenticated_client_with_db
    # subprefix = list(router.source.keys())
    # language = router.languages
    routers = ((route.path, route.response_model) for route in routers_get if 'handbook' in route.path)
    for prefix, response_model in routers:
        print('++++++++++++++++++++', prefix, response_model)
        response = await client.get(prefix)
        # print(prefix, response_model.name)
        assert response.status_code == 200, response.text
        # result = response.json()
        # assert isinstance(result, dict)

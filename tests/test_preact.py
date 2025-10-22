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


async def test_preact_routers(authenticated_client_with_db, test_db_session,
                              fakedata_generator):
    from app.support.preact.router import prefix
    subprefixes = ['subregion', 'category']
    suffix = ['en', 'ru', 'fr']
    # генерируем роуты и сверяем их количество
    test_set = [f'/{prefix}/{a}/{b}' for a in subprefixes for b in suffix]
    expected_count = len(subprefixes) * len(suffix)
    assert len(test_set) == expected_count
    client = authenticated_client_with_db
    for pref in test_set:
        response = await client.get(pref)
        assert response.status_code == 200, f'роут "{pref}" работает некооректно. {response.text}'

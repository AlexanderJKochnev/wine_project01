# tests/test_search.py
"""
    тестируем все методы SEARCH
    новые методы добавляются автоматически
"""

from collections import Counter
from typing import Any, Dict, List  # NOQA: F401
from sqlalchemy import func, or_, select, and_, sql  # NOQA: F401
from sqlalchemy.sql import visitors
import pytest

from app.core.utils.common_utils import jprint  # NOQA: F401

pytestmark = pytest.mark.asyncio

txt_fields = ('description', 'title', 'subtitle', 'name', 'made_of', "recommendation")


def comprehensive_validation(filter_condition, model):
    """Комплексная проверка условия фильтрации"""

    # 1. Проверка типа
    if not isinstance(filter_condition, sql.ClauseElement):
        return False, "❌ Не является SQL выражением SQLAlchemy"

    # 2. Проверка ссылок на таблицы
    tables_referenced = set()

    def collect_tables(element):
        if hasattr(element, 'table'):
            tables_referenced.add(element.table)

    visitors.traverse(filter_condition, {}, {'column': collect_tables})

    model_table = model.__table__
    for table in tables_referenced:
        if table != model_table:
            return False, f"❌ Ссылка на чужую таблицу: {table}"

    # 3. Проверка синтаксиса через компиляцию
    try:
        test_stmt = sql.select(model).where(filter_condition).limit(1)
        _ = str(test_stmt.compile(compile_kwargs={"literal_binds": True}))
        print("✅ SQL компилируется без ошибок")
        return True, "✅ Условие корректно"
    except Exception as e:
        return False, f"❌ Ошибка компиляции: {e}"


def test_create_search_model():
    """
        test method create_search_model
        test method build_search_condition
        check sql request
    """
    from app.core.utils.alchemy_utils import create_search_model
    from app.support.drink.model import Drink as model
    from sqlalchemy import Column
    from sqlalchemy.orm import MapperProperty
    from sqlalchemy.orm.attributes import QueryableAttribute
    from app.core.utils.alchemy_utils import build_search_condition, create_search_conditions
    from sqlalchemy.dialects import postgresql
    # from app.support.drink.schemas import DrinkRead
    search_model = create_search_model(model)
    search_str: str = 'Some Words'
    conditions: list = []
    for key in search_model.model_fields.keys():
        # search_model возвращает поля из модели и ничего лишнего
        assert isinstance(getattr(model, key), (Column, MapperProperty, QueryableAttribute))
        assert getattr(model, key, None), f'{key} лишнее поле, ошибка метода create_search_model'
        # проверка метода build_search_condition
        field = getattr(model, key)
        condition = build_search_condition(field, search_str)
        conditions.append(condition)
    query = select(model).where(or_(*conditions))
    try:
        compiled_query = query.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})
        sql_text = str(compiled_query)
        print(sql_text)
    except Exception as e:
        assert False, f"Ошибка синтаксиса запроса на выборку: {e}"
    try:
        query = select(func.count()).select_from(model).where(or_(*conditions))
        compiled_query = query.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})
        sql_text = str(compiled_query)
        print(sql_text)
    except Exception as e:
        assert False, f"Ошибка синтаксиса запроса на подсчет записей: {e}"
    try:
        conditions = create_search_conditions(model, search_str)
        queries = {'select': select(model).where(or_(*conditions)),
                   'count': select(func.count()).select_from(model).where(or_(*conditions))}
        for key, val in queries.items():
            compiled_query = query.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})
            sql_text = str(compiled_query)
    except Exception:
        assert False, f'error in {key} query, {sql_text}'


@pytest.mark.skip
def test_get_text_model_fields():
    """
        тестирование метода get_text_model_fields
    """
    from app.support.drink.model import Drink
    from app.core.utils.common_utils import get_text_model_fields
    # from app.support.drink.repository import DrinkRepository
    model = Drink
    text_fields = get_text_model_fields(model)
    jprint(text_fields)
    search_query: str = 'search query'
    conditions = []
    for field in text_fields:
        conditions.append(getattr(model, field).ilike(f"%{search_query}%"))
    print(conditions)

    assert False


def test_create_search_conditions():
    from app.core.utils.alchemy_utils import create_search_conditions
    from app.support.drink.model import Drink as Model
    result = create_search_conditions(Model, 'test Search')
    # assert isinstance(result, list)
    condition = result  # (or_(*result))
    res, message = comprehensive_validation(condition, Model)
    assert res, message

# ------------------


def split_string(s: str, n: int = 3) -> List[str]:
    #  разбивает строку на список слов
    # return [s[i:i + n] for i in range(0, len(s), n)]
    return s.split(' ')


def count_and_sort_elements(input_list):
    """
    Преобразует список с повторяющимися элементами в список списков [элемент, количество],
    отсортированный по количеству повторов по убыванию.

    Args:
        input_list: список с повторяющимися элементами

    Returns:
        list: список списков формата [элемент, количество], отсортированный по количеству
    """
    # Считаем количество каждого элемента
    counter = Counter(input_list)

    # Сортируем элементы по количеству повторов (по убыванию)
    sorted_items = sorted(counter.items(), key=lambda x: x[1], reverse=True)

    # Преобразуем кортежи в списки
    result = [[item, count] for item, count in sorted_items]
    return result


def find_keys_by_word(data_dict: dict, search_word: str) -> list:
    """
    Находит ключи, значения которых содержат указанное слово.

    Args:
        data_dict: Словарь {key: value} где value - строки или None
        search_word: Слово для поиска

    Returns:
        List: Список ключей, содержащих слово в значениях
    """
    result = []
    search_word_lower = search_word.lower()
    for key, value in data_dict.items():
        if value is not None and search_word_lower in value.lower():
            result.append(key)

    return result


@pytest.mark.skip
async def test_search(authenticated_client_with_db, test_db_session,
                      routers_get_all, fakedata_generator):
    """ тестирует методы get one - c проверкой id """
    # from app.support.item.router import ItemRouter as Router
    from app.support.drink.router import DrinkRouter as Router
    client = authenticated_client_with_db
    # routers = routers_get_all
    routers = [Router().prefix,]
    # expected_response = PaginatedResponse.model_fields.keys()
    for prefix in routers:          # перебирает существующие роутеры
        if prefix in ['/api']:  # api не содержит пути 'all'
            continue
        response = await client.get(f'{prefix}/all')   # получает все записи
        assert response.status_code == 200, f'метод GET не работает для пути "{prefix}"'
        tmp: List[dict] = response.json()

        jprint(tmp)
        assert False

        tmp2: list = []
        exp: dict = {}
        for value in tmp:
            """ список всех слов """
            id = value['id']
            data: list = ' '.join((val for key, val in value.items()
                                   if isinstance(val, str) and key not in ['created_at', 'updated_at'])
                                  ).split(' ')
            exp[id] = ' '.join(data)
            tmp2.extend(data)
        tmp2 = count_and_sort_elements(tmp2)
        query, expected_nmbr = tmp2[0]
        expected_answer = find_keys_by_word(exp, query)
        params = {'query': query}

        response = await client.get(f'{prefix}/search', params=params)
        assert response.status_code == 200
        result = response.json()
        items = result.get('items')
        ids = [val['id'] for val in items]
        assert sorted(ids) == sorted(expected_answer), f'{ids=} {expected_answer=} {query=} {prefix=}'

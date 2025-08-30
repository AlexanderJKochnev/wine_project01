# tests/test_create.py
"""
    валидация генерируемых тестовых данных
    проверка метода POST
    новые методы добавляются автоматически
"""

import pytest
from app.core.schemas.base import ListResponse  # noqa: F401

pytestmark = pytest.mark.asyncio


async def test_input_validation(authenticated_client_with_db,
                                test_db_session,
                                routers_get_all,
                                # fakedata_generator,
                                routers_post):
    # client = authenticated_client_with_db
    # from app.support.drink.router import DrinkRouter as Router
    from app.support.customer.router import CustomerRouter as Router
    data = {'category_id': 1,
            'color_id': 1,
            'sweetness_id': 1,
            'region_id': 1,
            'subtitle': 'East Mallorystad',
            'alcohol': 2.97, 'sugar': 1.3, 'aging': 3, 'sparkling': False,
            'food': ['Ellenfurt',],
            'description': 'Cause hotel right nice movement her. '
                           'Themselves perform anything could. '
                           'Red already vote us effort.\nMemory environment follow type machine. '
                           'Bed you maybe group.',
            'description_ru': 'Where language book. Scene person short realize rise star argue you.'
                              '\nYou me short design act beat bank. Onto year by.\nTen plan let store. '
                              'Computer grow cell newspaper charge.',
            'name_ru': 'Daniel Jensen', 'name': 'Charles Mills'}
    data = {'login': 'Lake Cathyfurt', 'id': 1}
    router = Router()
    # prefix = router.prefix
    create_schema = router.create_schema
    try:
        _ = create_schema(**data)
    except Exception as e:
        assert False, f'Ошибка валидации {e}, {data}'

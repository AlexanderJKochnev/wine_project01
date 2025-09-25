# tests/test_create_mongo.py
"""
проверка методов mongo+postgres
"""

import pytest
from pydantic import TypeAdapter
import json
from app.core.utils.common_utils import jprint
pytestmark = pytest.mark.asyncio


async def test_new_data_generator_relation(authenticated_client_with_db, test_db_session, sample_image_paths):
    """ валидация генерируемых данных со связанными полями и загрузка """
    from tests.data_factory.fake_generator import generate_test_data
    from app.support.drink.router import DrinkRouter as Router
    from app.support.drink.schemas import DrinkCreateRelations
    source = [Router]  # simple_router_list + complex_router_list
    
    test_number = len(sample_image_paths)
    client = authenticated_client_with_db
    for n, item in enumerate(source):
        router = item()
        schema = router.create_schema_relation
        adapter = TypeAdapter(schema)
        prefix = router.prefix
        # генератор тестовых данных для postgresql
        test_data = generate_test_data(
            schema, test_number,
            {'int_range': (1, test_number),
             'decimal_range': (0.5, 1),
             'float_range': (0.1, 1.0),
             # 'field_overrides': {'name': 'Special Product'},
             'faker_seed': 42}
        )

        for m, data in enumerate(test_data):
            try:
                # _ = schema(**data)      # валидация данных
                json_data = json.dumps(data)
                adapter.validate_json(json_data)
                assert True
            except Exception as e:
                assert False, f'Error IN INPUT VALIDATION {e}, router {prefix}, example {m}'
            # генератор тествых данных для mongodb
            with open(sample_image_paths[m], 'rb') as f:
                test_image_data = f.read()
            # test_image_data = b"fake_image_876876876876_data"
            files = {"file": (f"test_{m}.jpg", test_image_data, "image/jpeg")}
            
            try:
                # Отправляем данные в поле "data" как JSON строку
                form_data = {"data": json.dumps(data)}
            except Exception as e:
                assert False, e
            try:
                response = await client.post(f'{prefix}/full', data=form_data, files=files)
                assert response.status_code in [200, 201], response.text  # response["message"] == "Image uploaded successfully", response
            except Exception as e:
                # jprint(data)
                if 'response' in locals():
                    print(f"Response status: {response.status_code=}")
                    print(f"Response text: {response.text=}")
                assert False, e


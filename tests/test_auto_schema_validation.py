import pytest
from tests.utility.schema_validator import SchemaValidator
from tests.utility.find_models import discover_models

pytestmark = pytest.mark.asyncio


async def test_get_all_schemas_from_openapi(authenticated_client_with_db, test_db_session):
    client = authenticated_client_with_db
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    openapi = response.json()

    # Все компоненты (включая схемы)
    schemas = openapi["components"]["schemas"]
    print("Все модели в OpenAPI:")
    for schema_name, schema_def in schemas.items():
        print(f"- {schema_name}: {schema_def.get('description', '')} {type(schema_def)}")


def test_all_models_have_tablename(authenticated_client_with_db, test_db_session):
    models = discover_models()
    assert len(models) > 0, "Не найдено ни одной ORM-модели"
    for model in models:
        assert hasattr(model, "__tablename__"), f"Модель {model.__name__} не имеет __tablename__"


async def test_auto_schema_validation(test_models, get_schemas):
    """Автоматическая валидация всех схем и моделей"""
    try:
        all_errors = []
        print(f'{get_schemas=}')
        for model in test_models:
            model_name = model.__name__
            if model_name in get_schemas:
                errors = SchemaValidator.validate_schema_model_compatibility(
                    model, get_schemas[model_name]
                )
                all_errors.extend([f"{model_name}: {error}" for error in errors])
            else:
                all_errors.append(f"{model_name}: No schemas found")

        assert not all_errors, "Schema validation errors:\n" + "\n".join(all_errors)
    except Exception as e:
        assert False, f'ошибка!!!!!  {e}'


@pytest.mark.asyncio
async def test_auto_schema_properties(get_schemas):
    """Автоматическая проверка свойств схем"""
    errors = []

    for model_name, schemas in get_schemas.items():
        # Проверяем Create схему
        if 'create' in schemas:
            create_fields = schemas['create'].__annotations__.keys()
            if 'id' in create_fields:
                errors.append(f"{model_name} Create schema contains 'id' field")

        # Проверяем Update схему
        if 'update' in schemas:
            for field_name, field_type in schemas['update'].__annotations__.items():
                if not SchemaValidator._is_optional_type(field_type):
                    errors.append(f"{model_name} Update field {field_name} is not optional")

    assert not errors, "Schema property errors:\n" + "\n".join(errors)

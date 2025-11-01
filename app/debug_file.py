# debug_services.py
import sys


def check_imports():
    print("=== ПРОВЕРКА ИМПОРТОВ ===")

    try:
        from app.support.drink.service import DrinkService
        print("✅ DrinkService импортирован успешно")
        print(f"   __abstract__: {getattr(DrinkService, '__abstract__', 'NOT_SET')}")
    except Exception as e:
        print(f"❌ Ошибка импорта DrinkService: {e}")
        import traceback
        traceback.print_exc()

    try:
        from app.support.item.service import ItemService
        print("✅ ItemService импортирован успешно")
        print(f"   __abstract__: {getattr(ItemService, '__abstract__', 'NOT_SET')}")
    except Exception as e:
        print(f"❌ Ошибка импорта ItemService: {e}")
        import traceback
        traceback.print_exc()

    print("\n=== РЕГИСТРАЦИЯ В METACLASS ===")
    from app.core.services.service import ServiceMeta
    for key, service_class in ServiceMeta._registry.items():
        print(f"   {key}: {service_class.__name__}")


def verify_registration():
    print("\n=== ПРОВЕРКА РЕГИСТРАЦИИ ===")
    
    from app.core.services.service import ServiceMeta
    
    print("Все зарегистрированные сервисы:")
    for key, service_class in ServiceMeta._registry.items():
        is_abstract = getattr(service_class, '__abstract__', False)
        status = "ABSTRACT" if is_abstract else "CONCRETE"
        print(f"  {key:15} -> {service_class.__name__:20} [{status}]")
    
    # Проверьте, доступны ли сервисы через registry
    drink_service = ServiceMeta._registry.get('drink')
    item_service = ServiceMeta._registry.get('item')
    
    print(f"\nDrinkService доступен через registry: {drink_service is not None}")
    print(f"ItemService доступен через registry: {item_service is not None}")


def check_metaclass_instances():
    print("\n=== ПРОВЕРКА МЕТАКЛАССА ===")
    
    from app.core.services.service import ServiceMeta, Service
    
    print(f"ServiceMeta: {ServiceMeta}")
    print(f"Service.__class__: {Service.__class__}")
    print(f"ServiceMeta._registry id: {id(ServiceMeta._registry)}")
    print(f"ServiceMeta._registry: {ServiceMeta._registry}")
    
    # Проверьте все классы Service
    print("\nВсе классы с метаклассом ServiceMeta:")
    for cls in ServiceMeta._registry.values():
        print(f"  {cls.__name__} -> {cls.__class__}")


if __name__ == "__main__":
    check_imports()
    verify_registration()
    check_metaclass_instances()
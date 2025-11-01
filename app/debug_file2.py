# debug_comparison.py
from app.support.subcategory.service import SubcategoryService  # ✅ Регистрируется
from app.support.drink.service import DrinkService  # ❌ Не регистрируется
from app.support.item.service import ItemService  # ❌ Не регистрируется


def compare_services():
    print("=== СРАВНЕНИЕ СЕРВИСОВ ===")
    
    services = {'SubcategoryService': SubcategoryService, 'DrinkService': DrinkService, 'ItemService': ItemService}
    
    for name, service in services.items():
        print(f"\n🔍 {name}:")
        print(f"   __module__: {service.__module__}")
        print(f"   __bases__: {service.__bases__}")
        print(f"   __abstract__: {getattr(service, '__abstract__', 'NOT_SET')}")
        print(f"   __class__: {service.__class__}")
        print(f"   MRO: {service.__mro__}")
        
        # Проверяем атрибуты метакласса
        if hasattr(service, '_registry'):
            print(f"   _registry: {service._registry}")


def check_metaclass_identity():
    from app.support.subcategory.service import SubcategoryService
    from app.support.drink.service import DrinkService
    from app.support.item.service import ItemService
    from app.core.services.service import ServiceMeta
    
    print("=== ПРОВЕРКА МЕТАКЛАССА ===")
    print(f"ServiceMeta: {id(ServiceMeta)}")
    print(f"SubcategoryService.__class__: {id(SubcategoryService.__class__)}")
    print(f"DrinkService.__class__: {id(DrinkService.__class__)}")
    print(f"ItemService.__class__: {id(ItemService.__class__)}")
    
    print(f"SubcategoryService использует ServiceMeta: {SubcategoryService.__class__ is ServiceMeta}")
    print(f"DrinkService использует ServiceMeta: {DrinkService.__class__ is ServiceMeta}")
    print(f"ItemService использует ServiceMeta: {ItemService.__class__ is ServiceMeta}")



compare_services()

check_metaclass_identity()

from typing import Dict, Any, List, Set, Tuple


def compare_dict_structures(
        reference: Dict[str, Any], test: Dict[str, Any], path: str = ""
) -> List[str]:
    """
    Сравнивает структуры двух вложенных словарей и возвращает отличия.

    Args:
        reference: Эталонный словарь
        test: Тестируемый словарь
        path: Текущий путь в структуре (для рекурсивных вызовов)

    Returns:
        Список строк с описанием отличий
    """
    differences = []

    # Проверка всех ключей из эталонного словаря
    for key, ref_value in reference.items():
        current_path = f"{path}.{key}" if path else key

        # Проверка наличия ключа
        if key not in test:
            differences.append(f"Отсутствует ключ: {current_path}")
            continue

        test_value = test[key]
        ref_type = type(ref_value)
        test_type = type(test_value)

        # Проверка типа данных
        if ref_type != test_type:
            # Особый случай: числа (int/float) могут быть совместимы
            if not ((ref_type in [int, float] and test_type in [int, float]) or (
                    ref_type in [str, type(None)] and test_type in [str, type(None)])):
                differences.append(
                    f"Несовпадение типов в {current_path}: "
                    f"ожидался {ref_type.__name__}, получен {test_type.__name__}"
                )
                continue

        # Рекурсивная проверка для вложенных словарей
        if isinstance(ref_value, dict) and isinstance(test_value, dict):
            differences.extend(compare_dict_structures(ref_value, test_value, current_path))

        # Рекурсивная проверка для списков
        elif isinstance(ref_value, list) and isinstance(test_value, list):
            if ref_value and test_value:
                # Проверяем структуру первого элемента списка
                if isinstance(ref_value[0], dict) and isinstance(test_value[0], dict):
                    differences.extend(
                        compare_dict_structures(ref_value[0], test_value[0], f"{current_path}[0]")
                    )
                elif type(ref_value[0]) != type(test_value[0]):
                    differences.append(
                        f"Несовпадение типов элементов в {current_path}: "
                        f"ожидался {type(ref_value[0]).__name__}, "
                        f"получен {type(test_value[0]).__name__}"
                    )
            elif ref_value and not test_value:
                differences.append(f"Пустой список: {current_path}")

    # Проверка на лишние ключи в тестовом словаре
    extra_keys = set(test.keys()) - set(reference.keys())
    for extra_key in extra_keys:
        current_path = f"{path}.{extra_key}" if path else extra_key
        differences.append(f"Лишний ключ: {current_path}")

    return differences


def get_structure_differences(reference: Dict[str, Any], test: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Анализирует различия между эталонной и тестовой структурой.

    Returns:
        Словарь с категоризированными отличиями
    """
    all_differences = compare_dict_structures(reference, test)

    result = {"missing_keys": [], "type_mismatches": [], "extra_keys": [], "other_issues": []}

    for diff in all_differences:
        if diff.startswith("Отсутствует ключ:"):
            result["missing_keys"].append(diff)
        elif diff.startswith("Несовпадение типов"):
            result["type_mismatches"].append(diff)
        elif diff.startswith("Лишний ключ:"):
            result["extra_keys"].append(diff)
        else:
            result["other_issues"].append(diff)

    return result


# Пример использования
if __name__ == "__main__":
    # Ваши данные
    reference_structure = {
        "image_path": "string",
        "subcategory": {
            "category": {
                "name": "string",
                "description": "string",
                "description_ru": "string",
                "description_fr": "string",
                "name_ru": "string",
                "name_fr": "string"
            },
            "name": "string",
            "description": "string",
            "description_ru": "string",
            "description_fr": "string",
            "name_ru": "string",
            "name_fr": "string"
        },
        "sweetness": {
            "name": "string",
            "description": "string",
            "description_ru": "string",
            "description_fr": "string",
            "name_ru": "string",
            "name_fr": "string"
        },
        "subregion": {
            "region": {
                "country": {
                    "name": "string",
                    "description": "string",
                    "description_ru": "string",
                    "description_fr": "string",
                    "name_ru": "string",
                    "name_fr": "string"
                },
                "name": "string",
                "description": "string",
                "description_ru": "string",
                "description_fr": "string",
                "name_ru": "string",
                "name_fr": "string"
            },
            "name": "string",
            "description": "string",
            "description_ru": "string",
            "description_fr": "string",
            "name_ru": "string",
            "name_fr": "string"
        },
        "title": "string",
        "title_native": "string",
        "subtitle_native": "string",
        "subtitle": "string",
        "recommendation": "string",
        "recommendation_ru": "string",
        "recommendation_fr": "string",
        "madeof": "string",
        "madeof_ru": "string",
        "alc": 0,
        "sugar": 0,
        "aging": 0,
        "age": "string",
        "sparkling": True,
        "foods": [
            {
                "name": "string",
                "description": "string",
                "description_ru": "string",
                "description_fr": "string",
                "name_ru": "string",
                "name_fr": "string"
            }
        ],
        "varietals": [
            {
                "varietal": {
                    "name": "string",
                    "description": "string",
                    "description_ru": "string",
                    "description_fr": "string",
                    "name_ru": "string",
                    "name_fr": "string"
                },
                "percentage": 0,
                "additionalProp1": {}
            }
        ],
        "description": "string",
        "description_ru": "string",
        "description_fr": "string"
    }

    test_structure = {
        "alc": 13.5,
        "description": "Intense, concentrated and deep ruby-colored, this wine offers elegant, complex aromas of red fruits. In the mouth it is rich and dense, but harmonious, with sweet, balanced tannins. \nThe wine has a long finish with a depth and structure that ensure its extraordinary longevity.",
        "subtitle": "Tenuta San Guido",
        "title": "Bolgheri Sassicaia 2014 DOC",
        "varietal": [
            {
                "name": "Cabernet Sauvignon",
                "percentage": 85.0
            },
            {
                "name": "Cabernet Franc",
                "percentage": 15.0
            }
        ],
        "vol": 0.75,
        "description_ru": "Насыщенное, полнотелое вино, глубокого рубинового оттенка предлагает элегантные, сложные ароматы красных фруктов. Вино имеет богатый и плотный, но гармоничный вкус, со сладкими, сбалансированными танинами. \nОбладает послевкусием с глубиной и структурой, обеспечивающей его необычайную продолжительность.",
        "subtitle_ru": "Tenuta San Guido",
        "title_ru": "Bolgheri Sassicaia 2014 DOC",
        "varietal_ru": [
            {
                "name_ru": "каберне совиньон",
                "percentage": 85.0
            },
            {
                "name_ru": "каберне фран",
                "percentage": 15.0
            }
        ],
        "img_path": "-Lymluc5yKRoLQyYLbJG",
        "subregion": {
            "name": "",
            "name_ru": None,
            "region": {
                "name": "Madeira",
                "name_ru": "Мадейра",
                "country": {
                    "name": "Portugal",
                    "name_ru": None
                }
            }
        },
        "subcategory": {
            "name": "",
            "name_ru": None,
            "category": {
                "name": "Port",
                "name_ru": None
            }
        },
        "foods": [
            {
                "name": "Game (venison)",
                "name_ru": "С дичью"
            },
            {
                "name": "Lamb",
                "name_ru": "Бараниной"
            }
        ],
        "varietals": [
            {
                "varietal": {
                    "name": "Cabernet Sauvignon",
                    "name_ru": "каберне совиньон"
                },
                "percentage": 85.0
            },
            {
                "varietal": {
                    "name": "Cabernet Franc",
                    "name_ru": "каберне фран"
                },
                "percentage": 15.0
            }
        ]
    }

    # Сравнение структур
    differences = get_structure_differences(reference_structure, test_structure)

    print("=== РЕЗУЛЬТАТЫ СРАВНЕНИЯ ===")

    if any(differences.values()):
        print("\nОтсутствующие ключи:")
        for diff in differences["missing_keys"]:
            print(f"  - {diff}")

        print("\nНесовпадения типов:")
        for diff in differences["type_mismatches"]:
            print(f"  - {diff}")

        print("\nЛишние ключи:")
        for diff in differences["extra_keys"]:
            print(f"  - {diff}")

        print("\nДругие проблемы:")
        for diff in differences["other_issues"]:
            print(f"  - {diff}")
    else:
        print("Структуры полностью совпадают!")

from app.core.utils.converters import convert_dict1_to_dict2  # , convert_dict2_to_dict1
from app.core.utils.io_utils import get_filepath_from_dir_by_name, readJson
from app.core.utils.common_utils import jprint
from app.support.item.schemas import ItemCreateRelation, DrinkCreateRelation  # noqa: F401


def test_convers():
    filepath = get_filepath_from_dir_by_name('test.json')
    dict1 = readJson(filepath)
    assert isinstance(dict1, dict), type(dict1)
    convers = convert_dict1_to_dict2(dict1)
    assert isinstance(convers, dict), type(convers)
    # jprint(convers)
    # assert False
    for key, val in convers.items():
        try:
            model = ItemCreateRelation(**val)
            back_dict = model.model_dump()
            assert val == back_dict
        except Exception as e:
            jprint(val)
            print(e)
            assert False


def test_dict_compair():
    dict1 = {
        "-Lymluc5yKRoLQyYLbJG": {
            "count": 0,
            "vol": 0.75,
            "drink": {
                "alc": 13.5,
                "description": "Intense, concentrated and deep ruby-colored, this wine offers elegant, complex aromas of red fruits. In the mouth it is rich and dense, but harmonious, with sweet, balanced tannins. \nThe wine has a long finish with a depth and structure that ensure its extraordinary longevity.",
                "foods": [
                    {
                        "name": "Game (venison, birds)",
                        "name_ru": "с дичью"
                    },
                    {
                        "name": "Lamb.",
                        "name_ru": "бараниной."
                    }
                ],
                "subregion": {
                    "name": "Bolgheri",
                    "name_ru": "Болгери",
                    "region": {
                        "name": "Tuscany",
                        "name_ru": "Тоскана",
                        "country": {
                            "name": "Italy",
                            "name_ru": None
                        }
                    }
                },
                "subtitle": "Tenuta San Guido",
                "title": "Bolgheri Sassicaia 2014 DOC",
                "varietals": [
                    {
                        "varietal": {
                            "name": "Cabernet Sauvignon 8",
                            "name_ru": "8"
                        },
                        "percentage": 5.0
                    },
                    {
                        "varietal": {
                            "name": "Cabernet Franc 1",
                            "name_ru": "1"
                        },
                        "percentage": 5.0
                    }
                ],
                "description_ru": "Насыщенное, полнотелое вино, глубокого рубинового оттенка предлагает элегантные, сложные ароматы красных фруктов. Вино имеет богатый и плотный, но гармоничный вкус, со сладкими, сбалансированными танинами. \nОбладает послевкусием с глубиной и структурой, обеспечивающей его необычайную продолжительность.",
                "subtitle_ru": "Тенута Сан Гвидо",
                "title_ru": "Болгери Сассициана 2014 DOC",
                "vol_ru": "0.75 l"
            }
        }
    }
    dict2 = {
        "-Lymluc5yKRoLQyYLbJG": {
            "vol": 0.75,
            "drink": {
                "alc": 13.5,
                "description": "Intense, concentrated and deep ruby-colored, this wine offers elegant, complex aromas of red fruits. In the mouth it is rich and dense, but harmonious, with sweet, balanced tannins. The wine has a long finish with a depth and structure that ensure its extraordinary longevity.",
                "subtitle": "Tenuta San Guido",
                "title": "Bolgheri Sassicaia 2014 DOC",
                "description_ru": "Насыщенное, полнотелое вино, глубокого рубинового оттенка предлагает элегантные, сложные ароматы красных фруктов. Вино имеет богатый и плотный, но гармоничный вкус, со сладкими, сбалансированными танинами. Обладает послевкусием с глубиной и структурой, обеспечивающей его необычайную продолжительность.",
                "subtitle_ru": "Тенута Сан Гвидо",
                "title_ru": "Болгери Сассициана 2014 DOC",
                "subregion": {
                    "name": "Bolgheri",
                    "name_ru": "Болгери",
                    "region": {
                        "name": "Tuscany",
                        "name_ru": "Тоскана",
                        "country": {
                            "name": "Italy",
                            "name_ru": None
                        }
                    }
                },
                "subcategory": {
                    "name": "Red",
                    "name_ru": None,
                    "category": {
                        "name": "Wine",
                        "name_ru": None
                    }
                },
                "foods": [
                    {
                        "name": "Game (venison, birds)",
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
                            "name_ru": "Каберне Совиньон"
                        },
                        "percentage": 85.0
                    },
                    {
                        "varietal": {
                            "name": "Cabernet Franc",
                            "name_ru": "Каберне Фран"
                        },
                        "percentage": 15.0
                    }
                ]
            },
            "count": 0,
            "image_path": "-Lymluc5yKRoLQyYLbJG.png"
        }}
    assert dict1 == dict2
